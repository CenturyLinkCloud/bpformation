# -*- coding: utf-8 -*-
"""
Manage Blueprints.
"""

import os
import re
import sys
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

	
	"""
	        <div class="blueprint-specs">
			    <div class="price">$37.37/month</div>
			    <div>$0.05/hour</div>
			    <div>
	Ubuntu 14 64-bit                                            </div>
			    <div class="left-col">1 server</div>
			    <div>1 cpu</div>
			    <div class="left-col">2 GB memory</div>
			    <div>17 GB storage</div>
		    </div>
	    </div>
	</div></li>
	        <li ><div id="2371" class="tile tile-blueprint">
	<input id="UUID" name="UUID" type="hidden" value="83627c9c-1354-4ef3-b99c-6d9e475b956c" />
	    <div class="blueprint-info">
	        <a href="/blueprints/browser/details/2371">
	            <div class="blueprint-desc">
				    <div><strong>Complete Pivotal Greenplum setup.  Includes master, standby master, and 2 service nodes.  Deploys 8 CPUs, 32GB RAM, and 2TB disk across 6 segments.</strong></div>
				    <hr>
				    <div class="left-col">visibility</div>
				    <div class="right-col"><strong>private</strong></div>
				    <em>Feb 17, 2015</em>
			    </div>
	        </a>
	        <div class="blueprint-header">
		        <label>DEV Pivotal Greenplum - 4 node small cluster</label>
		        <div class="author">by CSA Tools</div>
		        <div id="star-rating-83627c9c-1354-4ef3-b99c-6d9e475b956c" class="star-rating">
	    <input id="StarID" name="StarID" type="hidden" value="83627c9c-1354-4ef3-b99c-6d9e475b956c" />
	    <input id="StarRating" name="StarRating" type="hidden" value="0" />
	    <input id="Active" name="Active" type="hidden" value="False" />
	</div>
	"""
	@staticmethod
	def List(filters):
		"""
		Search-Author:
		Search-PageSize:9
		Search-PageNumber:2
		LastSort:1
		Search-Keyword:
		AccountAlias:--ALL--
		Accounts:--ALL--
		Accounts:-1
		Category:-1
		OS:-1
		CompanySize:-
		"""
		r = bpformation.web.CallScrape("POST","/blueprints/browser/LoadTemplates",payload={
					'Search-PageSize': 1000,
					'Search-PageNumber': 1,
				}).text
		print r

		#table = re.search('id="PackageLibrary">.*?<table class="table">.*?<tbody>(.*)</tbody>',r,re.DOTALL).group(1)

		blueprints = []
		for blueprint_html in filter(lambda x: x in Blueprint.limited_printable_chars, r).split('class="blueprint-specs"'):
			cols = package_html.split("<td>")
			try:
				blueprints.append({'name': re.search('\s*(.+?)\s*<input',cols[1],re.DOTALL).group(1),
				                 'uuid': re.search('<input id="package_UUID" name="package.UUID" type="hidden" value="(.*?)"\s*/>',cols[1],re.DOTALL).group(1),
						         'owner': re.search('(.*?)</td>',cols[2]).group(1),
						         'status': re.search('</i>(.+?)</td>',cols[3]).group(1),
						         'visibility': re.search('\s*(.+?)\s*</td>',cols[4]).group(1) })
				
				print blueprints
				sys.exit()
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




