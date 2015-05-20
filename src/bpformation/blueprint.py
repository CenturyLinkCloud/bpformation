# -*- coding: utf-8 -*-
"""
Manage Blueprints.
"""

import os
import re
import sys
import json
import time
from lxml import objectify, etree

import bpformation


#
# TODO vCur:
#  o Delete
#  o Export
#  o Import
#  o Create
#  o Change


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

	
	@staticmethod
	def Export(id):
		bp = {'metadata': {}, 'servers': []}
		# TODO - Blueprint metadata

		# Blueprint definition
		r = bpformation.web.CallScrape("GET","/Blueprints/Designer/BlueprintXml/%s" % id)
		if r.status_code<200 or r.status_code>=300:
			bpformation.output.Status('ERROR',3,"Error retrieving data (http response %s)" % r.status_code)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		t = etree.XML(r.text)
		for build_server in t.findall(".//BuildServer"):
			server = { 'name': build_server.get("Alias"), 'uuid': build_server.get("UUID"), 'description': build_server.get("Description"),
					   'id': build_server.get("ID"), 'template': build_server.get("Template"), 'cpu': build_server.get("CpuCount"), 
					   'ram': build_server.get("MemoryGB"), 'disks': [], 'packages': [] }
			#for attr, value in build_server.items():
			#	if attr in ('Title','UUID','Template','Alias','Description','MemoryGB','CpuCount','ID'):
			#		server[attr] = value
			#	print(' * %s = %s' % (attr, value))
			bp['servers'].append(server)

		#print json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': '))


	# Available, but not returning:
	#  o Price information
	#  o Environment size details (server count, memory, CPU, etc.)
	#  o Blueprint description
	@staticmethod
	def List(filters):
		r = bpformation.web.CallScrape("POST","/blueprints/browser/LoadTemplates",payload={
					'Search-PageSize': 1000,
					'Search-PageNumber': 1,
				}).text

		blueprints = []
		for blueprint_html in filter(lambda x: x in Blueprint.limited_printable_chars, r).split('class="blueprint-specs"'):
			try:
				blueprints.append({'name': re.search('class="blueprint-header">.*<label>(.+?)</label>',blueprint_html).group(1),
						           'owner': re.search('<div class="author">by (.+?)</div>',blueprint_html).group(1),
								   'date_added': re.search('<em>(.+?)</em>',blueprint_html).group(1),
								   'description': re.search('<div class="blueprint-desc">\s*<div><strong>(.+?)</strong>',blueprint_html).group(1),
								   'visibility': re.search('<div class="right-col"><strong>(.+?)</strong></div>',blueprint_html).group(1),
						           'id': re.search('<a href="/blueprints/browser/details/(\d+)">',blueprint_html).group(1) })
				
			except:
				pass

		# Apply filters if any are specified
		if not filters:  blueprints_final = blueprints
		else:
			blueprints_final = []
			for blueprint in blueprints:
				match = True
				for one_filter in filters:
					if not re.search(one_filter," ".join(blueprint.values()),re.IGNORECASE):  match = False
				if  match:  blueprints_final.append(blueprint)

		return(blueprints_final)




