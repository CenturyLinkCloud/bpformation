# -*- coding: utf-8 -*-
"""
Manage Blueprint packages.
"""

import os
import re
import clc
import time
import ftplib
import requests
import bpformation


#
# TODO vCur:
#  o Query for all parameters associated with a package.  Optionally enforce on package Execute
#


#
# TODO vNext:
#  o Create new ftp endpoint if none exists
#  o Retrive list of existing packages using v2 json endpoint
#


class Package():

	visibility_stoi = { 'Public': 1, 'Private': 2, 'Shared': 3}
	limited_printable_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~  "


	@staticmethod
	def _GetFtpEndpoint():
		# TODO - alert on failure to locate.  Maybe add scrape POST call to create if missing?

		# Scrape from ftp users page
		#text = bpformation.web.CallScrape("GET","/Blueprints/ftpuser").text
		#m = re.search("%s_BlueprintUser</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>" % bpformation.web.Alias(),text,re.DOTALL)

		#if m:
		#	bpformation.FTP_ENDPOINT = {'user': "%s_BlueprintUser" % bpformation.web.Alias(), 
		#	                            'passwd': m.group(1), 'endpoint': m.group(2)}
		#	bpformation.output.Status('SUCCESS',1,"FTP endpoint %s@%s cached" % (bpformation.FTP_ENDPOINT['user'],bpformation.FTP_ENDPOINT['endpoint']))
		#else:  bpformation.output.Status('ERROR',3,"Unable to retrieve FTP endpoint.  Make sure %s_BlueprintUser exists" % bpformation.web.Alias())
		# json response direct form scripts page

		r = bpformation.web.CallScrape("POST","/blueprints/packages/GetFTPDetails").json()
		bpformation.FTP_ENDPOINT = {'user': r['userName'], 'passwd': r['password'], 'endpoint': r['ftpHost']}
		bpformation.output.Status('SUCCESS',1,"FTP endpoint %s@%s cached" % (bpformation.FTP_ENDPOINT['user'],bpformation.FTP_ENDPOINT['endpoint']))



	@staticmethod
	def Upload(files):
		for file in files:
			if not os.path.isfile(file):
				bpformation.output.Status('ERROR',3,"Package file '%s' not found" % file)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		if not bpformation.FTP_ENDPOINT:  Package._GetFtpEndpoint()

		# TODO - alert nicely on login failure
		# TODO - output xfer stats if verbose
		ftp = ftplib.FTP(bpformation.FTP_ENDPOINT['endpoint'],bpformation.FTP_ENDPOINT['user'],bpformation.FTP_ENDPOINT['passwd'])
		for file in files:
			time_start = time.time()
			with open(file,'rb') as fh:
				file_name = re.sub(".*/","",file)
				ftp.storbinary("STOR %s" % (file_name),fh)
			bpformation.output.Status('SUCCESS',3,"%s successfully uploaded (%s seconds)" % (file_name,int(time.time()-time_start)))
		ftp.quit()

	
	@staticmethod
	def _PackageOSAtoI(type,os_regexs):
		# TODO - catch error
		oss = bpformation.web.CallScrape("POST","/blueprints/packages/GetOSList", {'osType': type}).json()['Result']

		oss_retain = {}
		for os_regex in os_regexs:  
			if re.match("rhel",os_regex.lower()):  os_regex = "RedHat"
			for os in oss:  
				if re.search(os_regex,os['Name']):  oss_retain[os['ID']] = True

		return(oss_retain.keys())

	
	@staticmethod
	def ListOS(type):
		try:
			return(bpformation.web.CallScrape("POST","/blueprints/packages/GetOSList", {'osType': type}).json()['Result'])
		except:
			bpformation.output.Status('ERROR',3,"Unable to retrieve OS listi")
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))


	@staticmethod
	def Publish(files,type,visibility,os):
		task_queue = []
		for file in files:
			r = bpformation.web.CallScrape("POST","/Blueprints/Packages/Properties",
							               payload={"packageName": file,
									                "Type": 2,
									                "OS": type,
									                "Permissions": Package.visibility_stoi[visibility],
									                "OS_Version": Package._PackageOSAtoI(type,os)})
			if r.status_code>=200 and r.status_code<400:
				m = re.search("<a href=\"/Blueprints/Queue/RequestDetails/(\d+)\?location=(.+)\"",r.text)
				task_queue.append({'id': int(m.group(1)), 'location': m.group(2), 'description': file, 'date_added': time.time()})
				bpformation.output.Status('SUCCESS',3,"%s publish job submitted" % file)
			elif re.search("Unable to publish software package. .*A new UUID is required",r.text):
				bpformation.output.Status('ERROR',3,"Unable to publish %s. A new UUID is required" % file)
			else:
				bpformation.output.Status('ERROR',3,"Unknown error publishing %s (http response code %s)" % (file,r.status_code))
				

		bpformation.queue.WaitForQueue(task_queue)

		if visibility.lower()=="public":
			bpformation.output.Status('SUCCESS',3,"CenturyLink approval needed for Public publishing.  Email ecosystem@CenturyLinkCloud.com for approval")

	
	@staticmethod
	def Delete(uuids):
		for uuid in uuids:
			r = bpformation.web.CallScrape("POST","/blueprints/packages/DeletePackage/",
							               payload={"id": uuid, "classification": "Script", })
			if r.status_code<400 and r.status_code>=200:
				bpformation.output.Status('SUCCESS',3,"%s package deleted" % uuid)
			else:
				bpformation.output.Status('ERROR',3,"%s package deletion error (status code %s)" % (uuid,r.status_code))

	
	@staticmethod
	def Download(uuids):
		if not bpformation._CONTROL_COOKIES:  bpformation.web._LoginScrape()

		for uuid in uuids:
			r = requests.get("%s/Blueprints/Packages/Download?uuid=%s" % (bpformation.defaults.CONTROL_URL,uuid), 
			                 cookies=bpformation._CONTROL_COOKIES,
							 stream=True)
			try:
				with open("%s.zip" % uuid, 'wb') as f:
					for chunk in r.iter_content(chunk_size=1024):
						if re.search("You do not have permissions to download this package\.",chunk):
							raise(Exception("Insufficient permissions to download"))
						elif chunk: # filter out keep-alive new chunks
							f.write(chunk)
							f.flush()
				bpformation.output.Status('SUCCESS',3,"%s package downloaded" % uuid)
			except:
				bpformation.output.Status('ERROR',3,"Insufficient permissions to download %s" % uuid)
				try:
					os.remove("%s.zip")
				except:
					pass


	
	@staticmethod
	def List(filters):
		# TODO - Query json v2 endpoint - https://control.ctl.io/api/tunnel/v2/packages/$alias
		r = bpformation.web.CallScrape("GET","/Blueprints/packages/Library").text
		table = re.search('id="PackageLibrary">.*?<table class="table">.*?<tbody>(.*)</tbody>',r,re.DOTALL).group(1)

		packages = []
		for package_html in filter(lambda x: x in Package.limited_printable_chars, table).split("</tr>"):
			#m = re.search('<td>\s*(.+?)\s*<input id="package_UUID".*?value="(.+?)".*?<td>(.*?)</td>.*?<td>.*(.+?)</td>i.*</i>(.*?)</td>.*<td>.*\s(.+?)\s*</td>',package_html,re.DOTALL)
			cols = package_html.split("<td>")
			try:
				packages.append({'name': re.search('\s*(.+?)\s*<input',cols[1],re.DOTALL).group(1),
				                 'uuid': re.search('<input id="package_UUID" name="package.UUID" type="hidden" value="(.*?)"\s*/>',cols[1],re.DOTALL).group(1),
						         'owner': re.search('(.*?)</td>',cols[2]).group(1),
						         'status': re.search('</i>(.+?)</td>',cols[3]).group(1),
						         'visibility': re.search('\s*(.+?)\s*</td>',cols[4]).group(1) })
				
			except:
				pass
			#print m.group(0)
			#if m:  packages.append({'name': m.group(1), 'uuid': m.group(2), 'owner': m.group(3), 'visibility': m.group(4)})

		# Apply filters if any are specified
		if not filters:  packages_final = packages
		else:
			packages_final = []
			for package in packages:
				match = True
				for one_filter in filters:
					if not re.search(one_filter," ".join(package.values()),re.IGNORECASE):  match = False
				if  match:  packages_final.append(package)

		return(packages_final)


	@staticmethod
	def Execute(uuid,servers,parameters):
		# TODO - async option
		clc.v2.SetCredentials(bpformation.CONTROL_USER, bpformation.CONTROL_PASSWORD)
		requests = []
		start_time = time.time()
		for server in servers:
			bpformation.output.Status('SUCCESS',3,"Execution request submitted for %s" % server.lower())
			if parameters:  parameters = dict( (p.split("=")[0],p.split("=",1)[1]) for p in parameters )
			else:  parameters=None
			requests.append(clc.v2.Server(server,alias=bpformation.web.Alias()).ExecutePackage(
					package_id=re.sub("[^a-zA-Z0-9]","",uuid).lower(),   # Wants uuid w/o dashes
					parameters=parameters,
				))

		requests = sum(requests)
		requests.WaitUntilComplete()
		if len(requests.success_requests):
			success_servers = [ o.data['context_val'] for o in requests.success_requests ]
			bpformation.output.Status('SUCCESS',3,"Execution completed on %s (%s seconds)" % (", ".join(success_servers),int(time.time()-start_time)))
		for request in requests.error_requests:
			(req_loc,req_id) = request.id.split("-",1)
			r = bpformation.web.CallScrape("GET","/Blueprints/Queue/RequestDetails/%s?location=%s" % (req_id,req_loc))
			if r.status_code<300 and r.status_code>=200:
				error = re.search('<div class="module-body">.*?<pre>(\s*.Error.\s*)?(.*?)\s*</pre>',r.text,re.DOTALL).group(2)
				bpformation.output.Status('ERROR',3,"Execution failed on %s: %s" % (request.data['context_val'],error))
			else:
				bpformation.output.Status('ERROR',3,"Execution failed on %s request ID %s (https://control.ctl.io/Blueprints/Queue/RequestDetails/%s?location=%s)" % \
						(request.data['context_val'],req_id,req_id,req_loc))



