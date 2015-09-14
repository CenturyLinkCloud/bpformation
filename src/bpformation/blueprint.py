# -*- coding: utf-8 -*-
"""
Manage Blueprints.
"""

import os
import re
import sys
import clc
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
			else:  bpformation.output.Status('ERROR',3,"Error unknown server tag '%s'" % o.tag)

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
			# Not currently supported: Reboot outside of build server
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

		# Populate server name/id dict
		servers = {}
		for o in t.xpath("//Parameter"):
			if o.get("Type") == "ServerAlias":
				servers[o.get("Default")] = o.get("Variable").replace(".Alias","")

		# Populate Blueprint execute stub with script-specific vals
		server_names = {}
		for o in t.findall("UI/Group"):  
			# system params - we don't replicate
			if o.get("Name") == "Build Server":  continue

			elif o.get("Name") == "Global Blueprint Values":  
				for param in o.findall("Parameter"):  
					if param.get("Default"):  default = param.get("Default")
					elif param.get("Type") in ("Option","MultiSelect"):
						default = " | ".join([ opt.get("Value") for opt in param.findall("Option") ])
					else:  default = ''
					bp['execute'][param.get("Variable")] = default

			# Assume all other els are groups containing local package-specific variables
			else:
				for param in o.findall("Parameter"):  
					if param.get("Default"):  default = param.get("Default")
					elif param.get("Type") in ("Option","MultiSelect"):
						default = " | ".join([ opt.get("Value") for opt in param.findall("Option") ])
					elif re.search("\.TaskServer$",param.get("Variable")):
						default = " | ".join([ o for o in servers.keys() ])
					else:  default = ''
					bp['execute'][param.get("Variable")] = default

		# Output
		if file=="-":  
			print json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': '))
		else:
			if file is None:  file = "%s-%s-%s.json" % (re.sub("[^a-zA-Z0-9\-_]","_",bp['metadata']['name']).lower(),id,bp['metadata']['version'])
			bpformation.output.Status('SUCCESS',3,"%s v%s exported to %s (%s tasks)" % (bp['metadata']['name'],bp['metadata']['version'],file,len(bp['tasks'])))
			with open(file,'w') as fh:
				fh.write(json.dumps(bp,sort_keys=True,indent=4,separators=(',', ': ')))


	# Available, but we aren't returning:
	#  o Price information
	#  o Environment size details (server count, memory, CPU, etc.)
	#  o Blueprint description
	@staticmethod
	def List(filters,accounts=None):
		if accounts is None:  accounts = ""
		else:  accounts = ",".join(accounts)

		r = bpformation.web.CallScrape("POST","/blueprints/browser/filter",payload={
					'Search-PageSize': 1000,
					'Search-PageNumber': 1,
					'AccountAlias': accounts,
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
		if len(o['name'])==0 or len(o['name'])>6:
			bpformation.output.Status('ERROR',3,"Blueprint json server name must be between 0 and six characters")
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
		if 'tasks' in o:
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

				# System - set ttl
				#elif task['type']=='ttl' and task['uuid']=='2d4d37e6-be83-461a-bfd2-b3c2ca327db5':
				#	staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']
				#	staged_tasks['Server.Tasks[%s].Properties[0].Name' % staged_tasks_idx] = 'ActivityType'
				#	staged_tasks['Server.Tasks[%s].Properties[0].Value' % staged_tasks_idx] = 'Delete'
				#	staged_tasks['Server.Tasks[%s].Properties[1].Name' % staged_tasks_idx] = 'TimeZone'
				#	staged_tasks['Server.Tasks[%s].Properties[1].Value' % staged_tasks_idx] = 'UTC'
				#	staged_tasks['Server.Tasks[%s].Properties[2].Name' % staged_tasks_idx] = 'ScheduleDate'
				#	staged_tasks['Server.Tasks[%s].Properties[2].Value' % staged_tasks_idx] = '2015-06-06T15:35:00Z'
	
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
		r = bpformation.web.CallScrape("POST","/blueprints/designer/SaveServer?id=%s" % blueprint_id,allow_redirects=False,payload=dict({
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

		if o['id']==0:  o['id'] = r.json()['serverID']
		return(o)


	@staticmethod
	def _PostTask(blueprint_id,o):
		"""
		Post to create/update add-on tasks.

		Must include all parameters for the server - anything not specified is "deleted".

		o is a server object with keys name, description, cpu, ram, template, id, and a list of tasks.
		o['id'] is 0 for new servers, otherwise include the uuid of the existing server to modify.
		"""

		"""
		Tasks appear to be preserved (unlike other attrs) on write.  So since we don't want to take control
		state as authoritative at any time we first delete tasks.  After delete we add tasks in the order
		specified.

		POST https://control.ctl.io/blueprints/designer/DeleteTask
		id:3710
		taskId:d858c386-112e-4fae-9fd2-9129bdeaa1e8

		POST https://control.ctl.io/blueprints/designer/AddTasks?id=3708
		id=3708
		Tasks[0].Properties[0].Value:SpecifyAtDeployment
		Tasks[0].Properties[0].Name:Server
		Tasks[0].ID:77ab3844-579d-4c8d-8955-c69a94a2ba1a


		Alternatly - make sure each specified task exists, then issue a reorder statement at the end?
		"""

		# Build tasks data structure
		# TODO - query for parameters and verify we meet requirements
		staged_tasks = {}
		staged_tasks_idx = 0 
		if 'tasks' in o:
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

				# System - set ttl
				#elif task['type']=='ttl' and task['uuid']=='2d4d37e6-be83-461a-bfd2-b3c2ca327db5':
				#	staged_tasks['Server.Tasks[%s].ID' % staged_tasks_idx] = task['uuid']
				#	staged_tasks['Server.Tasks[%s].Properties[0].Name' % staged_tasks_idx] = 'ActivityType'
				#	staged_tasks['Server.Tasks[%s].Properties[0].Value' % staged_tasks_idx] = 'Delete'
				#	staged_tasks['Server.Tasks[%s].Properties[1].Name' % staged_tasks_idx] = 'TimeZone'
				#	staged_tasks['Server.Tasks[%s].Properties[1].Value' % staged_tasks_idx] = 'UTC'
				#	staged_tasks['Server.Tasks[%s].Properties[2].Name' % staged_tasks_idx] = 'ScheduleDate'
				#	staged_tasks['Server.Tasks[%s].Properties[2].Value' % staged_tasks_idx] = '2015-06-06T15:35:00Z'
	
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
		r = bpformation.web.CallScrape("POST","/blueprints/designer/SaveServer?id=%s" % blueprint_id,allow_redirects=False,payload=dict({
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

		if o['id']==0:  o['id'] = r.json()['serverID']
		return(o)


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

		# Step 0 - Get UUID if existing
		if bp['metadata']['id']:
			r = bpformation.web.CallScrape("GET","/blueprints/browser/details/%s" % bp['metadata']['id'])
			if r.status_code<200 or r.status_code>=300:
				bpformation.output.Status('ERROR',3,"Error creating blueprint - step 0 uuid failure (response %s)" % r.status_code)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
			bp['metadata']['uuid'] = re.search('/Blueprints/Browser/Clone.blueprintUUID=([a-zA-Z0-9\-]+)',r.text,re.DOTALL).group(1)
			r = bpformation.web.CallScrape("GET","/blueprints/designer/metadata/%s" % bp['metadata']['uuid'],allow_redirects=False)
		else:  bp['metadata']['uuid'] = str(uuid.uuid4())

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
		r = bpformation.web.CallScrape("POST","/Blueprints/Designer/review/%s" % bp['metadata']['id'],allow_redirects=False,payload={
					"Publish": "", # unknown
					"DataTemplate.UUID": bp['metadata']['uuid'],
					"TemplateID": bp['metadata']['id'],
				})

		# TODO Step 4 - save output?  Assume needed for some kind of update

		if bp['metadata']['visibility'].lower()=="public":  
				bpformation.output.Status('SUCCESS',3,"CenturyLink approval needed for Public publishing.  Email ecosystem@CenturyLinkCloud.com for approval")

		return(bp)


	@staticmethod
	def Import(files):
		bp_ids = []
		for file in files:
			if not os.path.isfile(file):
				bpformation.output.Status('ERROR',3,"Blueprint json file '%s' not found" % file)

			# Load json
			with open(file) as fh:  bp = json.load(fh)

			# Strip unique IDs from assets that will be duplicated
			bp['metadata']['id'] = 0
			new_tasks = []
			for task in bp['tasks']:  new_tasks.append(Blueprint._ImportAnonymizeTasks(task))
			bp['tasks'] = new_tasks
				
			# Publish BP, obtain BP with ids as result
			bp = Blueprint._PostBlueprint(bp)
			bpformation.output.Status('SUCCESS',3,"%s v%s imported ID %s (%s tasks)" % (bp['metadata']['name'],bp['metadata']['version'],bp['metadata']['id'],len(bp['tasks'])))
			#bpformation.output.Status('SUCCESS',3,"Blueprint created with ID %s (https://control.ctl.io/blueprints/browser/details/%s)" % (blueprint_id,blueprint_id))
			bp_ids.append(bp['metadata']['id'])

		return(bp_ids)


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
	def Execute(ids,files,parameters,type,password,group_id,network,dns):
		"""

		parameters - dict of key/value pairs or a list of key=value pairs
		"""

		# Build list of file-based assets to exec
		bps = []
		if files is not None and len(files):
			for file in files:
				if not os.path.isfile(file):
					bpformation.output.Status('ERROR',3,"Blueprint json file '%s' not found" % file)
	
				# Load json
				with open(file) as fh:
					bp = json.load(fh)
	
				if 'id' not in bp['metadata']:
					bpformation.output.Status('ERROR',3,"No blueprint ID in '%s'" % file)
					raise(bpformation.BPFormationFatalExeption("Fatal Error"))
	
				bps.append({'execute': bp['execute'], 'id': bp['metadata']['id']})


		# Build list of id-based assets to exec
		if ids is not None and len(ids):
			for id in ids:  bps.append({'execute': {}, 'id': id})

		# Build execute parameter lists
		# order of precedence (low to high):
		#   o .bpformation ini file
		#   o blueprint json file 'execute' obj
		#   o command line args
		new_bps = []
		for bp in bps:
			# Refresh latest blueprint xml
			r = bpformation.web.CallScrape("GET","/Blueprints/Designer/BlueprintXml/%s" % bp['id'])
			if r.status_code<200 or r.status_code>=300:
				bpformation.output.Status('ERROR',3,"Error retrieving data (http response %s)" % r.status_code)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))
	
			t = etree.XML(r.text)

			# Populate server name/id dict
			servers = {}
			for o in t.xpath("//Parameter"):
				if o.get("Type") == "ServerAlias":
					servers[o.get("Default")] = o.get("Variable").replace(".Alias","")

			# Apply defaults from config file - don't overwrite existing items.  Only covers system items
			for key in ('type','password','group_id','network','dns'):
				if key in bp['execute']:  continue
				if bpformation.config and bpformation.config.has_option('blueprint_execute',key):  bp['execute'][key] = bpformation.config.get('blueprint_execute',key)

			# Apply system-level command line args
			for key in ('type','password','group_id','network','dns'):
				if key in vars() and vars()[key] is not None:  bp['execute'][key] = vars()[key]

			# Apply parameter command line args
			if parameters is not None and isinstance(parameters,dict):
				for key,value in parameters.items():  bp['execute'][key] = value
			elif parameters is not None and len(parameters):
				for parameter in parameters:
					(key,value) = parameter.split("=",1)
					bp['execute'][key] = value

			# If deploy-time server selection map to server.id
			for key,value in bp['execute'].items():
				# TODO - add and to except if explicit ID already provided
				if re.search("\.TaskServer$",key):
					bp['execute'][key] = [ "${%s.ServerName}" % id for alias,id in servers.items() if alias == value ][0]

			# Hardcoded default DNS - this is dumb that we ask for it
			if 'dns' not in bp['execute'] or not len(bp['execute']['dns']):
				bp['execute']['dns'] = "172.17.1.26"

			# Confirm system parameters are all set
			for key in ('type','password','group_id','network','dns'):
				if key not in bp['execute'] or not len(bp['execute'][key]):
					bpformation.output.Status('ERROR',3,"Missing required system parameter '%s'" % key)
					raise(bpformation.BPFormationFatalExeption("Fatal Error"))

			# TODO Confirm all blueprint parameters are set

			# Rename system parameters so they match what POST is expecting
			bp['execute']['TemplateID'] = bp['id']
			bp['execute']['T3.BuildServerTask.Password'] = bp['execute']['password']
			bp['execute']['Confirm.T3.BuildServerTask.Password'] = bp['execute']['password']
			bp['execute']['T3.BuildServerTask.GroupID'] = bp['execute']['group_id']
			bp['execute']['T3.BuildServerTask.Network'] = bp['execute']['network']
			bp['execute']['T3.BuildServerTask.PrimaryDNS'] = 'Manual'
			bp['execute']['T3.BuildServerTask.PrimaryDNS_manual'] = bp['execute']['dns']
			bp['execute']['T3.BuildServerTask.SecondaryDNS'] = ''
			bp['execute']['T3.BuildServerTask.SecondaryDNS_manual'] = ''
			bp['execute']['T3.BuildServerTask.HardwareType'] = bp['execute']['type']
			bp['execute']['T3.BuildServerTask.AntiAffinityPoolId'] = ''
			bp['execute']['T3.BuildServerTask.ServiceLevel'] = 'Standard'
			bp['execute']['RequestID'] = ''
			bp['execute']['Submit'] = ''
			for key in ('password','group_id','network','dns','type'):  del(bp['execute'][key])

			new_bps.append(bp)
				
		bps = new_bps

		# Execute each Blueprint
		clc.v2.SetCredentials(bpformation.CONTROL_USER, bpformation.CONTROL_PASSWORD)
		results = {'servers': []}
		requests = []
		start_time = time.time()
		for bp in bps:
	
			# Step 1 - customize blueprint
			r = bpformation.web.CallScrape("POST","/Blueprints/Builder/Customize/%s" % bp['id'],allow_redirects=False,payload=bp['execute'])
			if r.status_code<200 or r.status_code>=400:
				bpformation.output.Status('ERROR',3,"Error executing blueprint - step 1 customization metadata failure (response %s)" % r.status_code)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))


			# Step 2 - deploy blueprint
			r = bpformation.web.CallScrape("POST",r.headers['location'],allow_redirects=False,payload={'TemplateID': bp['id'], 'Submit': ''})
			if r.status_code<200 or r.status_code>=400:
				bpformation.output.Status('ERROR',3,"Error executing blueprint - step 2 submit failure (response %s)" % r.status_code)
				raise(bpformation.BPFormationFatalExeption("Fatal Error"))

			# Step 3 - queue request id
			request_id = re.sub(".*/(\d+).*=(.*)",r'\2-\1',r.headers['location']).lower()
			requests.append(clc.v2.Requests([{'isQueued': True, 'links': [{'rel': 'status', 'id': request_id}]}],alias=bpformation.web.Alias()))
			bpformation.output.Status('SUCCESS',3,"Execution request submitted for Blueprint ID %s (request %s)" % (bp['id'],request_id))

		# Wait for executing blueprints to complete
		# TODO - async option
		requests = sum(requests)
		requests.WaitUntilComplete()
		if len(requests.success_requests):
			#bpformation.output.Status('SUCCESS',3,"Execution completed on %s (%s seconds)" % (",".join(success_servers),int(time.time()-start_time)))
			bpformation.output.Status('SUCCESS',3,"Execution completed on %s blueprints (%s seconds)" % (len(requests.success_requests),int(time.time()-start_time)))
			# Generate list of servers created
			try:
				for request in requests.success_requests:
					(req_loc,req_id) = request.id.split("-",1)
					r = bpformation.web.CallScrape("GET","/Blueprints/Queue/RequestDetails/%s?location=%s" % (req_id,req_loc))
					if r.status_code<300 and r.status_code>=200:
						# TODO - if multiople bps this will overwrite>  Need to merge
						results['servers'] = re.findall('<a href="/manage#/.+?/server/(.+?)">',r.text,re.DOTALL)
						bpformation.output.Status('SUCCESS',3,"The following server(s) were created: %s" % (", ".join(results['servers'])))
			except:
				pass

		for request in requests.error_requests:
			(req_loc,req_id) = request.id.split("-",1)
			r = bpformation.web.CallScrape("GET","/Blueprints/Queue/RequestDetails/%s?location=%s" % (req_id,req_loc))
			if r.status_code<300 and r.status_code>=200:
				error = re.search('<div class="module-body">.*?<pre>(\s*.Error.\s*)?(.*?)\s*</pre>',r.text,re.DOTALL).group(2)
				bpformation.output.Status('ERROR',3,"Execution failed on %s: %s" % (request.id,error))
			else:
				bpformation.output.Status('ERROR',3,"Execution failed on %s request ID %s (https://control.ctl.io/Blueprints/Queue/RequestDetails/%s?location=%s)" % \
						(request.data['context_val'],req_id,req_id,req_loc))

		if requests.error_requests:
			e = bpformation.BPFormationFatalExeption("Error executing blueprint")
			e.error_requests = requests.error_requests
			raise(e)

		return(results)

		# TODO - percolate error up so we exit with an error called as CLI or see exception as sdk


