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

	
	
	# TODO
	@staticmethod
	def PublishPackageScrape(files):
		bpformation.CallScrape("POST","/Blueprints/Packages/Properties",
						  payload={"packageName": "%s_%s.zip" % (package_ini.get("package","package"),package_ini.get("package","os")),
								   "Type": 2,
								   "OS": package_ini.get("package","os").title(),
								   "Permissions": 1,
								   "OS_Version": ["on",6,7,13,14,19,20,21,22,25,29,30,31,32,33,34,35,36,37,3839,41,42]})
		# TODO - call status with each callback.  
		#time.sleep(15) # wait for package publishing task to complete or it won't register with a new blueprint
		print "\tPackage published via screen scrape"


