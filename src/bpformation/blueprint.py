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


# TODO vCur:
#  o Import
#  o Delete
#  o Change


#
# TODO vNext:
#  o Create


class Blueprint():

	visibility_stoi = { 'public': 1, 'private': 2, 'shared': 3}
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
	def _ParseExportTaskDeployPackage(root):
		package_obj = {"type": "package", "id": root.get("ID"), "uuid": root.get("UUID"), "name": root.get("Title"), 'properties': {} }
		if root.get("Server"):  package_obj['server'] = root.get("Server")
		for prop in root.iter("Property"):
			package_obj['properties'][prop.get("Name")] = prop.get("Value")

		if not len(package_obj['properties'].keys()):  del(package_obj['properties'])
		return(package_obj)


	@staticmethod
	def _ParseExportTaskAddIPAddress(root):
		ip_obj = {"type": "add_ip", "id": root.get("ID"), "uuid": root.get("UUID") }
		return(ip_obj)


	@staticmethod
	def _ParseExportTaskAddMappedIPAddress(root):
		ip_obj = {"type": "add_nat_ip", "id": root.get("ID"), "uuid": root.get("UUID"),
		          "ingress_ports": root.get("FirewallOptions").split(", ") }
		return(ip_obj)


	@staticmethod
	def _ParseExportTaskReboot(root):
		ip_obj = {"type": "reboot", "id": root.get("ID"), "uuid": root.get("UUID") }
		return(ip_obj)


	@staticmethod
	def _ParseExportTaskAddDisk(root):
		disk_obj = {"type": "disk", "id": root.get("ID"), "uuid": root.get("UUID")}
		for prop in root[0]:
			if prop.get("Value")=="True":  disk_obj[prop.get("Name").lower()] = True
			elif prop.get("Value")=="False":  disk_obj[prop.get("Name").lower()] = False
			else:  disk_obj[prop.get("Name").lower()] = prop.get("Value")

		return(disk_obj)


	@staticmethod
	def _ParseExportTaskBuildServer(root):
		# Server foundation data
		server = { 'type': "server", 'name': root.get("Alias"), 'uuid': root.get("UUID"), 'description': root.get("Description"),
				   'id': root.get("ID"), 'template': root.get("Template"), 'cpu': root.get("CpuCount"), 
				   'ram': root.get("MemoryGB"), 'tasks': [] }

		for o in root:
			if o.tag=='DeployPackage':  server['tasks'].append(Blueprint._ParseExportTaskDeployPackage(o))
			elif o.tag=='AddDisk':  server['tasks'].append(Blueprint._ParseExportTaskAddDisk(o))
			elif o.tag=='AddIPAddress':  server['tasks'].append(Blueprint._ParseExportTaskAddIPAddress(o))
			elif o.tag=='AddMappedIPAddress':  server['tasks'].append(Blueprint._ParseExportTaskAddMappedIPAddress(o))
			elif o.tag=='Reboot':  server['tasks'].append(Blueprint._ParseExportTaskReboot(o))
			elif o.tag=='Properties':  continue
			else:  print "Unknown server tag: %s" % o.tag

		return(server)


	@staticmethod
	def _ExportProcessRoot(root):
		tasks = []
		if root.tag=="BuildServer":  tasks.append(Blueprint._ParseExportTaskBuildServer(root))
		elif root.tag=="DeployPackage":  tasks.append(Blueprint._ParseExportTaskDeployPackage(root))
		elif root.tag=="Blueprint":  
			for o in root:
				try:
					if o.tag != "Blueprint":  tasks.append(Blueprint._ExportProcessRoot(o)[0])
				except:
					# Catch only our exceptions
					pass
		else:  
			print "Unknown: %s" % root.tag
			raise(Exception("Unknown tag %s" % root.tag))

		return(tasks)


	@staticmethod
	def Export(id):
		bp = {'metadata': {}, 'tasks': [] }

		# Blueprint metadata 
		r = bpformation.web.CallScrape("GET","/blueprints/browser/details/%s" % id)
		if r.status_code<200 or r.status_code>=300:
			bpformation.output.Status('ERROR',3,"Error retrieving data (http response %s)" % r.status_code)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		bp['metadata'] = {
				'name': re.search('<h1 id="body-title" class="left">\s*(.+?)\s*<small>',r.text,re.DOTALL).group(1),
				'owner': re.search('<small>by (.+?)</small>',r.text).group(1),
				'version': re.search('<dt>version</dt>\s*<dd>\s*(.+?)\s*</dd>',r.text,re.DOTALL).group(1),
				'visibility': re.search('<dt>visibility</dt>\s*<dd>\s*(.+?)\s*-',r.text,re.DOTALL).group(1),
				'description': re.search('<div class="blueprint-price">.*?<p>\s*(.+?)\s*</p>',r.text,re.DOTALL).group(1),
			}

		# Blueprint definition
		r = bpformation.web.CallScrape("GET","/Blueprints/Designer/BlueprintXml/%s" % id)
		if r.status_code<200 or r.status_code>=300:
			bpformation.output.Status('ERROR',3,"Error retrieving data (http response %s)" % r.status_code)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		t = etree.XML(r.text)
		for o in t.findall("Tasks/*"):  
			try:
				bp['tasks'] += Blueprint._ExportProcessRoot(o)
			except:
					# Catch only our exceptions
				pass

		print json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': '))


	# Available, but not returning:
	#  o Price information
	#  o Environment size details (server count, memory, CPU, etc.)
	#  o Blueprint description
	@staticmethod
	def List(filters):
		# TODO - much of this is available with a json response as part of group execute package
		r = bpformation.web.CallScrape("POST","/blueprints/browser/LoadTemplates",payload={
					'Search-PageSize': 1000,
					'Search-PageNumber': 1,
				}).text

		blueprints = []
		for blueprint_html in filter(lambda x: x in Blueprint.limited_printable_chars, r).split('class="blueprint-specs"'):
			try:
				blueprints.append({'name': re.search('class="blueprint-header">.*<label>(.+?)</label>',blueprint_html).group(1),
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


	@staticmethod
	def _ExportAnonymizeTasks(o):
		if o['type'] == 'server' and 'uuid' in o: del(o['uuid'])
		if 'id' in o:  del(o['id'])
		if 'tasks' in o:
			for idx,task in enumerate(o['tasks']):
				o['tasks'][idx] = Blueprint._ExportAnonymizeTasks(task)

		return(o)


	@staticmethod
	def Import(files):
		for file in files:
			if not os.path.isfile(file):
				bpformation.output.Status('ERROR',3,"Blueprint json file '%s' not found" % file)

			# Load json
			with open(file) as fh:
				o = json.load(fh)

			# Strip unique IDs from assets that will be duplicated
			for idx,task in enumerate(o['tasks']):
				o['tasks'][idx] = Blueprint._ExportAnonymizeTasks(task)
				
			# Validate syntax and required metadata fields
			for key in ('description','name','visibility','version'):
				if key not in o['metadata']:
					bpformation.output.Status('ERROR',3,"Blueprint json missing metadata/%s" % key)
					raise(bpformation.BPFormationFatalExeption("Fatal Error"))

			# Munge version formatting
			if not re.search("^[\d\.]+$",o['metadata']['version']):  
				bpformation.output.Status('ERROR',3,"Blueprint json version must contain only a dotted number representation")
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
			m = re.search("(.+?)\.?(.*)",o['metadata']['version'])
			ver_major = int(m.group(1))
			if len(m.groups(2)):  ver_minor = int(m.group(2).replace(".",""))
			else:  ver_minor = 0

			# Metadata post and create Blueprint shell
			r = bpformation.web.CallScrape("POST","/blueprints/designer/metadata",allow_redirects=False,payload={
						"capabilities": "",     # Aligns to "tags"
						"companySize": 3,       # 1: 1-100, 2: 101-1,000, 3: 1001-5000, 4: 5,000+
						"isReseller": False,    # Tied to is_managed, no-op
						"templateID": 0,        # unknown
						"errors": [],           # unknown
						"userCapabilities": "", # TODO - Custom tags
						"description": o['metadata']['description'],
						"templateName": o['metadata']['name'],
						"visibility": Blueprint.visibility_stoi[o['metadata']['visibility'].lower()],
						"versionMajor": ver_major,
						"versionMinor": ver_minor,
					})
			if r.status_code<200 or >=300:
				bpformation.output.Status('ERROR',3,"Error creating blueprint - step 1 metadata failure (response %s") % r.status_code)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
			blueprint_id = r.json()['url']).group(1)



			#print json.dumps(o,sort_keys=True,indent=4,separators=(',', ': '))
			sys.exit()

			# Set metadata
			r = requests.post("https://control.ctl.io/blueprints/designer/metadata",
							  cookies=control_cookies,
							  data={"capabilities": "",
									"companySize": 3, 
									"description": package_ini.get("package","friendly_descr"),
									"errors": [],
									"isReseller": False,
									"templateID": 0,
									"templateName": "Install %s on %s" % (package_ini.get("package","friendly_name"),package_ini.get("package","os").title()),
									"userCapabilities": "Bitnami",
									"versionMajor": 1,
									"versionMinor": package_ini.get("system","change_count"),
									"visibility": 1})
			package_ini.set("system","blueprint_id",re.search("(\d+)$",r.json()['url']).group(1))
		
			# Save server config with package(s)
			if package_ini.get("package","os")=="linux":  
				payload = {"Server.ID": 0,
						   "Server.Template": config.get("clc","blueprint_template_%s_template" % package_ini.get("package","os")),
						   "Server.Name": package_ini.get("package","package")[:4],
						   "Server.Description": package_ini.get("package","friendly_name"),
						   "Server.Processor": config.get("clc","blueprint_template_%s_cpu" % package_ini.get("package","os")),
						   "Server.Memory": config.get("clc","blueprint_template_%s_ram" % package_ini.get("package","os")),
						   "Server.Tasks[0].ID": config.get("clc","blueprint_template_linux_update_uuid"),
						   "Server.Tasks[1].ID": package_ini.get("system","uuid")}
			else:
				payload = {"Server.ID": 0,
						   "Server.Template": config.get("clc","blueprint_template_%s_template" % package_ini.get("package","os")),
						   "Server.Name": package_ini.get("package","package")[:4],
						   "Server.Description": package_ini.get("package","friendly_name"),
						   "Server.Processor": config.get("clc","blueprint_template_%s_cpu" % package_ini.get("package","os")),
						   "Server.Memory": config.get("clc","blueprint_template_%s_ram" % package_ini.get("package","os")),
						   "Server.Tasks[0].ID": package_ini.get("system","uuid")}
			r = requests.post("https://control.ctl.io/blueprints/designer/SaveServer?id=%s" % package_ini.get("system","blueprint_id"),
							  cookies=control_cookies,data=payload)
		
			# Publish blueprint
			r = requests.post("https://control.ctl.io/Blueprints/Designer/Publish/%s" % package_ini.get("system","blueprint_id"),
							  cookies=control_cookies,
							  data={"TemplateID": package_ini.get("system","blueprint_id"),
									"DataTemplate.UUID": str(uuid.uuid4()),		# throw away value - not sure of purpose
							  		"Publish": ""})
			#print r.status_code
			#print r.text
		
			# Get blueprint uuid
			r = requests.get("https://control.ctl.io/blueprints/browser/details/%s" % package_ini.get("system","blueprint_id"),
							  cookies=control_cookies)
		
			package_ini.set("system","blueprint_uuid",re.search("/Blueprints/Designer/MetaData/(.+?)\"",r.text).group(1))
			print "\tNew Blueprint created and published via screen scrape"



