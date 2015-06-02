# -*- coding: utf-8 -*-
"""
Manage Blueprints.
"""

import os
import re
import sys
import uuid
import json
import time
from lxml import objectify, etree

import bpformation


# TODO vCur:


#
# TODO vNext:
#  o Create (via wizard)
#  o Blueprint package parameters - verify with /blueprints/designer/TaskParameters and alert on error
#  o Dependencies tree


class Blueprint():

	visibility_stoi = { 'public': 1, 'private': 2, 'shared': 3}
	limited_printable_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~  "


	@staticmethod
	def Delete(ids):
		for id in ids:
			# Lookup package uuid given id
			r = bpformation.web.CallScrape("GET","/blueprints/browser/details/%s" % id)
			try:
				name = re.search('<h1 id="body-title" class="left">\s*(.+?)\s*<small>',r.text,re.DOTALL).group(1)
				bp_uuid = re.search("/Blueprints/Designer/MetaData/(.+?)\"",r.text).group(1)
			except:
				bpformation.output.Status('ERROR',3,"Unable to location Blueprint %s (status code %s)" % (id,r.status_code))
				continue
				

			# Exec delete against uuid
			r = bpformation.web.CallScrape("POST","/blueprints/browser/delete", payload={"uuid": bp_uuid, })
			if r.status_code<400 and r.status_code>=200:
				bpformation.output.Status('SUCCESS',3,"%s deleted (id %s)" % (name,id))
			else:
				bpformation.output.Status('ERROR',3,"%s deletion error (status code %s)" % (id,r.status_code))


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
	def Export(id,file=None):
		# Silence status output if writing to stdout
		if file == "-":  bpformation.args.args.quiet = 999

		bp = {'metadata': {}, 'tasks': [], 'execute': {} }

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
				'id': id,
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

		# Populate Blueprint execute stub with script-specific vals
		for o in t.findall("UI/Group"):  
			if o.get("Name") == "Global Blueprint Values":  
				global_bp_values =  o
				break
		for o in global_bp_values.findall("Parameter"):  
			if o.get("Default"):  default = o.get("Default")
			elif o.get("Type") in ("Option","MultiSelect"):
				default = " | ".join([ opt.get("Value") for opt in o.findall("Option") ])
			else:  default = ''
			bp['execute'][o.get("Variable")] = default

		# Output
		if file=="-":  
			print json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': '))
		else:
			if file is None:  file = "%s-%s-%s.json" % (re.sub("[^a-zA-Z0-9\-_]","_",bp['metadata']['name']).lower(),id,bp['metadata']['version'])
			bpformation.output.Status('SUCCESS',3,"%s v%s exported to %s (%s tasks)" % (bp['metadata']['name'],bp['metadata']['version'],file,len(bp['tasks'])))
			with open(file,'w') as fh:
				fh.write(json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': ')))


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
	def _ImportAnonymizeTasks(o):
		if o['type'] == 'server' and 'uuid' in o: del(o['uuid'])
		if 'id' in o:  del(o['id'])
		if 'tasks' in o:
			for idx,task in enumerate(o['tasks']):
				o['tasks'][idx] = Blueprint._ImportAnonymizeTasks(task)

		return(o)


	@staticmethod
	def _PostServer(blueprint_id,o):
		"""
		Post to create/update server configuration.

		Must include all parameters for the server - anything not specified is "deleted".

		o is a server object with keys name, description, cpu, ram, template, id, and a list of tasks.
		o['id'] is 0 for new servers, otherwise include the uuid of the existing server to modify.
		"""

		# Validate core params
		for key in ('name','description','cpu','ram'):
			if key not in o:
				bpformation.output.Status('ERROR',3,"Blueprint json server definition missing '%s'" % key)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		if 'id' not in o:  o['id'] = 0	# New servers don't start with an ID
		if len(o['name'])==0 or len(o['name'])>5:
			bpformation.output.Status('ERROR',3,"Blueprint json server name must be between 0 and five characters" % key)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		if not re.match("^\d+$",o['cpu']) or int(o['cpu'])==0 or int(o['cpu'])>16:
			bpformation.output.Status('ERROR',3,"Blueprint json server cpu must be between 1 and 16" % key)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		if not re.match("^\d+$",o['ram']) or int(o['ram'])==0 or int(o['cpu'])>128:
			bpformation.output.Status('ERROR',3,"Blueprint json server ram must be between 1 and 128" % key)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		# Build tasks data structure
		# TODO - query for parameters and verify we meet requirements
		staged_tasks = {}
		staged_tasks_idx = 0 
		for task in o['tasks']:
			# TODO system tasks - scheduled task, delete snapshot, revert snapshot
			# System - add disk
			if task['type']=='disk' and task['uuid']=='22460210-b682-4138-93fd-1a95c5e4e039':
				staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']
				staged_tasks['Server.Tasks[%s].Properties[0].Name' % staged_tasks_idx] = 'GB'
				staged_tasks['Server.Tasks[%s].Properties[0].Value' % staged_tasks_idx] = task['gb']
				if 'drive' in task:
					staged_tasks['Server.Tasks[%s].Properties[1].Name' % staged_tasks_idx] = 'Drive'
					staged_tasks['Server.Tasks[%s].Properties[1].Value' % staged_tasks_idx] = task['drive']

			# System - reboot
			elif task['type']=='reboot' and task['uuid']=='5b949945-6981-4a81-bbcc-4ddd3d394b8d':
				staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']

			# System - add public NAT
			elif task['type']=='add_nat_ip' and task['uuid']=='c000d327-3543-4d9e-ac43-e8fbce4620ab':
				staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']
				staged_tasks['Server.Tasks[%s].Properties[0].Name' % staged_tasks_idx] = 'FirewallOptions'
				staged_tasks['Server.Tasks[%s].Properties[0].Value' % staged_tasks_idx] = ",".join(task['ingress_ports'])

			# System - add add'l private IP
			elif task['type']=='add_ip' and task['uuid']=='9a851f50-c676-4c11-b4c8-a0a7241c1060':
				staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']

			# User package
			elif task['type']=='package':
				staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']

				# Add all design-time parameters
				try:
					properties_idx = 0
					for key,value in task['properties'].items():
						staged_tasks['Server.Tasks[%s].Properties[%s].Name' % (staged_tasks_idx,properties_idx)] = key
						staged_tasks['Server.Tasks[%s].Properties[%s].Value' % (staged_tasks_idx,properties_idx)] = value
						properties_idx += 1
				except:
					pass

			# Unknown type/ID
			else:
				bpformation.output.Status('ERROR',3,"Blueprint json server task unknown type/id '%s'" % task['type'])
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))

			staged_tasks_idx += 1

		# Post
		r = bpformation.web.CallScrape("POST","/blueprints/designer/SaveServer",allow_redirects=False,payload=dict({
					"id": blueprint_id,
					"Server.ID": o['id'],
					"Server.Template": o['template'],
					"Server.Name": o['name'],
					"Server.Description": o['description'],
					"Server.Processor": o['cpu'],
					"Server.Memory": o['ram'],
				}.items() + staged_tasks.items()))
		if r.status_code<200 or r.status_code>=300:
			bpformation.output.Status('ERROR',3,"Error creating blueprint - step 2 add server failure (response %s)" % r.status_code)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		return(r.json()['serverID'])


	@staticmethod
	def _PostBlueprint(bp):
		"""Update and publish provided Blueprint objects."""

		# Validate syntax and required metadata fields
		for key in ('description','name','visibility','version'):
			if key not in bp['metadata']:
				bpformation.output.Status('ERROR',3,"Blueprint json missing metadata/%s" % key)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))

		# Munge version formatting
		if not re.search("^[\d\.]+$",bp['metadata']['version']):  
			bpformation.output.Status('ERROR',3,"Blueprint json version must contain only a dotted number representation")
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		m = re.search("(.+?)\.?(.*)",bp['metadata']['version'])
		ver_major = int(m.group(1))
		if len(m.groups(2)):  ver_minor = int(m.group(2).replace(".",""))
		else:  ver_minor = 0

		# Step 1 - Metadata post and create Blueprint shell
		r = bpformation.web.CallScrape("POST","/blueprints/designer/metadata",allow_redirects=False,payload={
					"capabilities": "",     # Aligns to "tags"
					"companySize": 3,       # 1: 1-100, 2: 101-1,000, 3: 1001-5000, 4: 5,000+
					"isReseller": False,    # Tied to is_managed, no-op
					"errors": [],           # unknown
					"userCapabilities": "", # TODO - Custom tags
					"templateID": bp['metadata']['id'],
					"description": bp['metadata']['description'],
					"templateName": bp['metadata']['name'],
					"visibility": Blueprint.visibility_stoi[bp['metadata']['visibility'].lower()],
					"versionMajor": ver_major,
					"versionMinor": ver_minor,
				})
		if r.status_code<200 or r.status_code>=300:
			bpformation.output.Status('ERROR',3,"Error creating blueprint - step 1 metadata failure (response %s)" % r.status_code)
			raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		bp['metadata']['id'] = re.search("(\d+)$",r.json()['url']).group(1)

		# Step 2 - Apply all tasks
		new_tasks = []
		for task in bp['tasks']:
			if task['type'] == 'server':  new_tasks.append(Blueprint._PostServer(bp['metadata']['id'],task))
			else:
				bpformation.output.Status('ERROR',3,"Unknown task type '%s'" % task['type'])
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
		bp['tasks'] = new_tasks

		# Step 3 - Publish Blueprint
		r = bpformation.web.CallScrape("POST","/Blueprints/Designer/Publish/%s" % bp['metadata']['id'],allow_redirects=False,payload={
					"Publish": "",                          # unknown
					"DataTemplate.UUID": str(uuid.uuid4()), # throw away value - not sure of purpose
				})

		# TODO Step 4 - save output?  Assume needed for some kind of update

		if bp['metadata']['visibility'].lower()=="public":  
				bpformation.output.Status('SUCCESS',3,"CenturyLink approval needed for Public publishing.  Email ecosystem@CenturyLinkCloud.com for approval")

		return(bp)


	@staticmethod
	def Import(files):
		for file in files:
			if not os.path.isfile(file):
				bpformation.output.Status('ERROR',3,"Blueprint json file '%s' not found" % file)

			# Load json
			with open(file) as fh:
				bp = json.load(fh)

			# Strip unique IDs from assets that will be duplicated
			bp['metadata']['id'] = 0
			new_tasks = []
			for task in bp['tasks']:  new_tasks.append(Blueprint._ImportAnonymizeTasks(task))
			bp['tasks'] = new_tasks
				
			# Publish BP, obtain BP with ids as result
			bp = Blueprint._PostBlueprint(bp)
			bpformation.output.Status('SUCCESS',3,"%s v%s imported ID %s (%s tasks)" % (bp['metadata']['name'],bp['metadata']['version'],bp['metadata']['id'],len(bp['tasks'])))
			#bpformation.output.Status('SUCCESS',3,"Blueprint created with ID %s (https://control.ctl.io/blueprints/browser/details/%s)" % (blueprint_id,blueprint_id))


	@staticmethod
	def Update(files):
		for file in files:
			if not os.path.isfile(file):
				bpformation.output.Status('ERROR',3,"Blueprint json file '%s' not found" % file)

			# Load json
			with open(file) as fh:
				bp = json.load(fh)

			# Publish BP, obtain BP with ids as result
			bp = Blueprint._PostBlueprint(bp)
			bpformation.output.Status('SUCCESS',3,"%s v%s updated ID %s (%s tasks)" % (bp['metadata']['name'],bp['metadata']['version'],bp['metadata']['id'],len(bp['tasks'])))
			#bpformation.output.Status('SUCCESS',3,"Blueprint created with ID %s (https://control.ctl.io/blueprints/browser/details/%s)" % (blueprint_id,blueprint_id))


	@staticmethod
	def _ExecuteMergeSystemParameters(type,password,group_id,network,dns):
		


	@staticmethod
	def Execute(id,files,parameters,type,password,group_id,network,dns):

		# TODO - find ids
		# TODO - verify any files specified exist and can be opened
		# TODO - foreach id/file - create merge payload
		# TODO - foreach id/file - execute

		# Superficial parameter validation
		if dns is None: dns = "172.17.1.26"

		"""
		POST https://control.ctl.io/Blueprints/Builder/Customize/3389
		TemplateID:3389
		T3.BuildServerTask.Password:Savvis11
		Confirm.T3.BuildServerTask.Password:Savvis11
		T3.BuildServerTask.GroupID:93cf0e58-9a38-448c-b0d7-c78f757c8874
		T3.BuildServerTask.Network:vlan_2314_10.50.14
		T3.BuildServerTask.PrimaryDNS:Manual
		T3.BuildServerTask.PrimaryDNS_manual:172.17.1.26
		T3.BuildServerTask.SecondaryDNS:
		T3.BuildServerTask.SecondaryDNS_manual:
		T3.BuildServerTask.HardwareType:Standard
		T3.BuildServerTask.AntiAffinityPoolId:
		T3.BuildServerTask.ServiceLevel:Standard
		72d04ebc-15fb-4cf9-b3c5-9acd33704824.Alias:X
		RequestID:
		Submit:
		--> 302 - /Blueprints/Builder/Review/26658

		GET https://control.ctl.io/Blueprints/Builder/Review/26658

		POST https://control.ctl.io/Blueprints/Builder/Review/26658
		TemplateID:3389
		Submit:
		--> 302 - /Blueprints/Queue/RequestDetails/26658?location=CA1

		GET https://control.ctl.io/Blueprints/Queue/RequestDetails/26658?location=CA1

		"""

