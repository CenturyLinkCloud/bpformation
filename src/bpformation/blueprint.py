# -*- coding: utf-8 -*-
"""
Manage Blueprints.
"""

import os
import re
import time

import bpformation


#
# TODO vCur:
#


#
# TODO vNext:
#


class Blueprint():

	#visibility_stoi = { 'Public': 1, 'Private': 2, 'Shared': 3}
	limited_printable_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~  "


#	@staticmethod
#	def Delete(uuids):
#		for uuid in uuids:
#			r = bpformation.web.CallScrape("POST","/blueprints/packages/DeletePackage/",
#							               payload={"id": uuid, "classification": "Script", })
#			if r.status_code<400 and r.status_code>=200:
#				bpformation.output.Status('SUCCESS',3,"%s package deleted" % uuid)
#			else:
#				bpformation.output.Status('ERROR',3,"%s package deletion error (status code %s)" % (uuid,r.status_code))

	
#	@staticmethod
#	def Download(uuids):
#		if not bpformation._CONTROL_COOKIES:  bpformation.web._LoginScrape()
#
#		for uuid in uuids:
#			r = requests.get("%s/Blueprints/Packages/Download?uuid=%s" % (bpformation.defaults.CONTROL_URL,uuid), 
#			                 cookies=bpformation._CONTROL_COOKIES,
#							 stream=True)
#			print r.status_code
#			with open("%s.zip" % uuid, 'wb') as f:
#				for chunk in r.iter_content(chunk_size=1024):
#					if chunk: # filter out keep-alive new chunks
#						f.write(chunk)
#						f.flush()
#			bpformation.output.Status('SUCCESS',3,"%s package downloaded" % uuid)

	
	@staticmethod
	def List(filters):
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




