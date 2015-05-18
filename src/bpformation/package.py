# -*- coding: utf-8 -*-
"""
Manage Blueprint packages.
"""

import os
import re
import time
import ftplib
import bpformation


#
# TODO vCur:
#  o Create new ftp endpoint if none exists
#  o Retrieve OS list.  Shortcut for "All Linux", "All Windows"
#  o Retrive list of existing packages.  Filter by metadata
#


#
# TODO vNext:
#


class Package():

	visibility_stoi = { 'Public': 1, 'Private': 2, 'Shared': 3}


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
			bpformation.output.Status('SUCCESS',3,"%s successfully uploaded in %s seconds" % (file_name,int(time.time()-time_start)))
		ftp.quit()

	
	@staticmethod
	def _PackageOSAtoI(type,os_regexs):
		# TODO - catch error
		oss = bpformation.web.CallScrape("POST","/blueprints/packages/GetOSList", {'osType': type}).json()['Result']

		oss_retain = {}
		for os_regex in os_regexs:  
			for os in oss:  
				if re.search(os_regex,os['Name']):  oss_retain[os['ID']] = True

		return(oss_retain.keys())

	
	@staticmethod
	def Publish(files,type,visibility,os):
		task_queue = []
		for file in files:
			r = bpformation.web.CallScrape("POST","/Blueprints/Packages/Properties",
							               payload={"packageName": file,
									                "Type": 2,
									                "OS": type,
									                "Permissions": Package.visibility_stoi[visibility],
									                "OS_Version": Package._PackageOSAtoI(type,os)}).text
			m = re.search("<a href=\"/Blueprints/Queue/RequestDetails/(\d+)\?location=(.+)\"",r)
			task_queue.append({'id': int(m.group(1)), 'location': m.group(2), 'description': file})
			bpformation.output.Status('SUCCESS',3,"%s publish job submitted" % file)

		bpformation.queue.WaitForQueue(task_queue)

	
	@staticmethod
	def Delete(uuids):
		for uuid in uuids:
			r = bpformation.web.CallScrape("POST","/blueprints/packages/DeletePackage/",
							               payload={"id": uuid, "classification": "Script", })
			if r.status_code<400 and r.status_code>=200:
				bpformation.output.Status('SUCCESS',3,"%s package deleted" % uuid)
			else:
				bpformation.output.Status('ERROR',3,"%s package deletion error (status code %s)" % (uuid,r.status_code))


