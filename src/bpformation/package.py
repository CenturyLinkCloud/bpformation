# -*- coding: utf-8 -*-
"""
Manage Blueprint packages.
"""

import os
import time
import ftplib
import bpformation


#
# TODO vCur:
#


#
# TODO vNext:
#


class Package():

	@staticmethod
	def _GetFtpEndpoint():
		# TODO - scrape ftp page and option user, password, and ftp endpoint associated with specified alias
		#        store data in bpformation.FTP_ENDPOINT object { user, passwd, endpoint} and cache for later use
		# TODO - alert on failure to locate.  Maybe add scrape POST call to create if missing?
		pass


	@staticmethod
	def UploadPackage(filename):
		if not bpformation.FTP_ENDPOINT:  Package._GetFtpEndpoint()

		if not os.path.isfile(filename):
			bpformation.output.Status('ERROR',3,"Package file '%s' not found" % filename)

		# TODO - alert nicely on login failure
		# TODO - output xfer stats if verbose
		time_start = time.time()
		ftp = ftplib.FTP(bpformation.FTP_ENDPOINT['endpoint'],bpformation.FTP_ENDPOINT['user'],bpformation.FTP_ENDPOINT['passwd'])
		with open(filename,'rb') as fh:
			file = re.sub(".*/","",filename)
			ftp.storbinary("STOR %s" % (file),fh)
		ftp.quit()

		bpformation.output.Status('SUCCESS',3,"Package successfully uploaded in %s seconds" % (int(time.time()-time_start)))
	
	
	@staticmethod
	def PublishPackageScrape(config,package_ini,filename):
		global control_cookies
	
		if not control_cookies:  _ControlLogin()
		r = requests.post("https://control.ctl.io/Blueprints/Packages/Properties",
						  cookies=control_cookies,
						  data={"packageName": "%s_%s.zip" % (package_ini.get("package","package"),package_ini.get("package","os")),
								"Type": 2,
								"OS": package_ini.get("package","os").title(),
								"Permissions": 1,
								"OS_Version": ["on",6,7,13,14,19,20,21,22,25,29,30,31,32,33,34,35,36,37,3839,41,42]})
		#time.sleep(15) # wait for package publishing task to complete or it won't register with a new blueprint
		print "\tPackage published via screen scrape"


