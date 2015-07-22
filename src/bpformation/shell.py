"""Command-line interface to the CenturyLink Cloud (CLC) API."""

import re
import os
import sys
import argparse
import ConfigParser

import bpformation


class Args:

	def __init__(self):
		bpformation.args = self
		self.ParseArgs()
		self.ImportIni()
		self.MergeEnvironment()
		self.MergeCommands()


	def ParseArgs(self):
		parser = argparse.ArgumentParser(description="CLI tool for interacting with CenturyLink Blueprints Package and Workflow Services.  http://www.CenturyLinkCloud.com (v%s)" % bpformation.__version__)
		parser_sp1 = parser.add_subparsers(title='Commands',dest='command')

		########## Package ###########
		#
		# TODO vCur:
		#
		# TODO vNext:
		#  o dependencies tree
		#  o package (zip given file manifest or directory.  Gen UUID.  Multiple options based on publish target)
		#

		parser_package = parser_sp1.add_parser('package', help='Package level activities (list, package, upload, publish, etc.)')
		parser_sp2 = parser_package.add_subparsers(dest='sub_command')

		## List
		parser_package_list = parser_sp2.add_parser('list', help='List package inventory')
		parser_package_list.add_argument('--filter', nargs='*', required=False, help='Regex filter Results by name, author, status, visibility (and)')

		## Upload
		parser_package_upload = parser_sp2.add_parser('upload', help='Uploaded package to specified alias')
		parser_package_upload.add_argument('--file', nargs='*', metavar="FILE", required=True, help='Files to upload')

		## List OS
		parser_package_listos = parser_sp2.add_parser('list-os', help='List known operating systems')
		parser_package_listos.add_argument('--type', required=True, choices=['Windows','Linux'], help='Operating system')

		## Publish
		parser_package_publish = parser_sp2.add_parser('publish', help='Uploaded packages to specified alias')
		parser_package_publish.add_argument('--file', nargs='*', required=True, help='Uploaded filename to process')
		parser_package_publish.add_argument('--type', required=True, choices=['Windows','Linux'], help='Operating system')
		parser_package_publish.add_argument('--visibility', required=True, choices=['Public','Private','Shared'], help='Package visibility')
		parser_package_publish.add_argument('--os', nargs='*', required=True, help='Operating system list (regex supported)')

		# Upload and publish
		parser_package_uploadpublish= parser_sp2.add_parser('upload-and-publish', help='Uploaded then publish packages to specified alias')
		parser_package_uploadpublish.add_argument('--file', nargs='*', metavar="FILE", required=True, help='Files to process')
		parser_package_uploadpublish.add_argument('--type', required=True, choices=['Windows','Linux'], help='Operating system')
		parser_package_uploadpublish.add_argument('--visibility', required=True, choices=['Public','Private','Shared'], help='Package visibility')
		parser_package_uploadpublish.add_argument('--os', nargs='*', required=True, help='Operating system list (regex supported)')

		## Delete
		parser_package_delete = parser_sp2.add_parser('delete', help='Delete published package')
		parser_package_delete.add_argument('--uuid', nargs='*', required=True, help='UUID for packages')

		## Download
		parser_package_download = parser_sp2.add_parser('download', help='Download published package')
		parser_package_download.add_argument('--uuid', nargs='*', required=True, help='UUID for packages')

		## Execute
		parser_package_execute = parser_sp2.add_parser('execute', help='Execute package')
		parser_package_execute.add_argument('--uuid', required=True, help='UUID for package')
		parser_package_execute.add_argument('--server', required=True, nargs='*', help='Servers targets for package execution')
		parser_package_execute.add_argument('--parameter', nargs='*', help='key=value pairs for package parameters')



		########## Blueprint ###########
		#
		# TODO vCur:
		#
		# TODO vNext:
		#  o create (interactive ui to build blueprint)
		#  o dependencies tree
		#

		parser_blueprint = parser_sp1.add_parser('blueprint', help='Blueprint level activities (list, import, export, delete, etc.)')
		parser_sp2 = parser_blueprint.add_subparsers(dest='sub_command')

		## List
		parser_blueprint_list = parser_sp2.add_parser('list', help='List blueprint inventory')
		parser_blueprint_list.add_argument('--filter', nargs='*', required=False, help='Regex filter Results by name, author, status, visibility (and)')
		parser_blueprint_list.add_argument('--account', nargs='*', required=False, help='One or more account alias authors to filter')

		## Export
		parser_blueprint_export = parser_sp2.add_parser('export', help='Export blueprint')
		parser_blueprint_export.add_argument('--id', required=True, help='Blueprint ID (note this ID is not globally unique - find this from your primary datacenter')
		parser_blueprint_export.add_argument('--file', required=False, help='Filename target for Blueprint json definition')

		## Import
		parser_blueprint_import = parser_sp2.add_parser('import', help='Import blueprint from json')
		parser_blueprint_import.add_argument('--file', nargs='*', required=True, help='Blueprint definition json files')

		## Update
		parser_blueprint_update = parser_sp2.add_parser('update', help='Update existing blueprint from json')
		parser_blueprint_update.add_argument('--file', nargs='*', required=True, help='Blueprint definition json files')

		## Delete
		parser_blueprint_delete = parser_sp2.add_parser('delete', help='Delete blueprint')
		parser_blueprint_delete.add_argument('--id', nargs='*', required=True, help='Blueprint ID (note this ID is not globally unique - find this from your primary datacenter')

		## Execute
		# TODO - update verbiage/grouping to make less confusing.  User can specify any combo of file, id, parameter, etc.
		#        as long as in the end they can be sensibly merged into a unified view that supplies all needed info.
		parser_blueprint_execute = parser_sp2.add_parser('execute', help='Execute blueprint')
		parser_blueprint_execute.add_argument('--file', nargs='*', help='Blueprint definition json files with "execute" populated')
		parser_blueprint_execute.add_argument('--id', nargs='*', help='Blueprint ID (note this ID is not globally unique - find this from your primary datacenter')
		parser_blueprint_execute.add_argument('--parameter', nargs='*', help='key=value pairs for package parameters (overrides "file")')
		parser_blueprint_execute.add_argument('--type', choices=['Standard','HyperScale'], help='Server hardware type')
		parser_blueprint_execute.add_argument('--password', help='Server deploy password')
		parser_blueprint_execute.add_argument('--group-id', help='Server deploy group ID')
		parser_blueprint_execute.add_argument('--network', help='Server deploy network')
		parser_blueprint_execute.add_argument('--dns', help='Server DNS')



		########## Global ###########
		#parser.add_argument('--cols', nargs='*', metavar='COL', help='Include only specific columns in the output')
		parser.add_argument('--config', '-c', help='Ini config file')
		parser.add_argument('--alias', '-a', help='Operate on specific account alias')
		parser.add_argument('--control-user', metavar='USER', help='Control username')
		parser.add_argument('--control-password', metavar='PASS', help='Control password')
		parser.add_argument('--quiet', '-q', default=1, action='count', help='Supress status output (repeat up to 2 times)')
		parser.add_argument('--verbose', '-v', action='count', help='Increase verbosity')
		parser.add_argument('--cols', nargs='*', metavar='COL', help='Include only specific columns in the output')
		parser.add_argument('--format', '-f', choices=['json','table','text','csv'], default='table', help='Output result format (table is default)')
		self.args = parser.parse_args()


	def GetCommand(self):  return(self.args.command)
	def GetArgs(self):  return(self.args)


	def ImportIni(self):
		config_file = False
		# Order of preference - cmd line specified, home directory file, or system file
		if self.args.config:
			config_file = self.args.config
			if self.args.config and not os.path.isfile(self.args.config):
				bpformation.output.Status('ERROR',3,"Config file %s not found" % (self.args.config))
				sys.exit(1)
		elif os.name=='nt':
			if os.path.isfile("%s/bpformation/bpformation.ini" % (os.getenv("PROGRAMDATA"))):
				config_file = "%s/bpformation/bpformation.ini" % (os.getenv("PROGRAMDATA"))
			elif os.path.isfile("bpformation.ini"):
				config_file = "bpformation.ini"
		else:
			if os.path.isfile("%s/.bpformation" % (os.environ['HOME'])):
				config_file = "%s/.bpformation" % (os.environ['HOME'])
			elif os.path.isfile("/usr/local/etc/bpformation_config"):
				config_file = "/usr/local/etc/bpformation_config"
		if config_file:  
			bpformation.output.Status('SUCCESS',0,"Reading %s" % (config_file))
			bpformation.config = ConfigParser.ConfigParser()
			bpformation.config.read(config_file)

			if bpformation.config.has_option('global','control_user'):  bpformation.CONTROL_USER = bpformation.config.get('global','control_user')
			if bpformation.config.has_option('global','control_password'):  bpformation.CONTROL_PASSWORD = bpformation.config.get('global','control_password')


	def MergeEnvironment(self):
		if 'CONTROL_USER' in os.environ:  bpformation.CONTROL_USER = os.environ['CONTROL_USER']
		if 'CONTROL_PASSWORD' in os.environ:  bpformation.CONTROL_PASSWORD = os.environ['CONTROL_PASSWORD']
		if 'ALIAS' in os.environ:  bpformation.ALIAS = os.environ['ALIAS']


	def MergeCommands(self):
		if self.args.control_user:  bpformation.CONTROL_USER = self.args.control_user
		if self.args.control_password:  bpformation.CONTROL_PASSWORD = self.args.control_password
		if self.args.alias:  bpformation.ALIAS = self.args.alias




class ExecCommand():
	def __init__(self):
		try:
			self.Bootstrap()
		except Exception as e:
			bpformation.output.Status("ERROR",3,"Exiting due to error: %s" % (str(e)))
			sys.exit(1)


	def Bootstrap(self):
		if bpformation.args.GetCommand() == 'package':  self.Package()
		elif bpformation.args.GetCommand() == 'blueprint':  self.Blueprint()


	def Package(self):
		if bpformation.args.GetArgs().sub_command == 'upload':  self.PackageUpload()
		elif bpformation.args.GetArgs().sub_command == 'list-os':  self.PackageListOS()
		elif bpformation.args.GetArgs().sub_command == 'publish':  self.PackagePublish()
		elif bpformation.args.GetArgs().sub_command == 'upload-and-publish':  self.PackageUploadAndPublish()
		elif bpformation.args.GetArgs().sub_command == 'delete':  self.PackageDelete()
		elif bpformation.args.GetArgs().sub_command == 'download':  self.PackageDownload()
		elif bpformation.args.GetArgs().sub_command == 'list':  self.PackageList()
		elif bpformation.args.GetArgs().sub_command == 'execute':  self.PackageExecute()


	def Blueprint(self):
		if bpformation.args.GetArgs().sub_command == 'list':  self.BlueprintList()
		elif bpformation.args.GetArgs().sub_command == 'export':  self.BlueprintExport()
		elif bpformation.args.GetArgs().sub_command == 'delete':  self.BlueprintDelete()
		elif bpformation.args.GetArgs().sub_command == 'import':  self.BlueprintImport()
		elif bpformation.args.GetArgs().sub_command == 'update':  self.BlueprintUpdate()
		elif bpformation.args.GetArgs().sub_command == 'execute':  self.BlueprintExecute()


	def PackageUpload(self):
		self.Exec('bpformation.package.Upload', {'files': bpformation.args.args.file}, cols=[])


	def PackagePublish(self):
		self.Exec('bpformation.package.Publish', {'files': bpformation.args.args.file, 'type': bpformation.args.args.type,
		                                          'visibility': bpformation.args.args.visibility, 'os': bpformation.args.args.os}, cols=[])


	def PackageUploadAndPublish(self):
		# Upload
		self.PackageUpload()

		# Publish
		bpformation.args.args.file = [re.sub(".*/","", o) for o in bpformation.args.args.file ]
		self.PackagePublish()


	def PackageDelete(self):
		self.Exec('bpformation.package.Delete', {'uuids': bpformation.args.args.uuid }, cols=[])


	def PackageDownload(self):
		self.Exec('bpformation.package.Download', {'uuids': bpformation.args.args.uuid }, cols=[])


	def PackageList(self):
		self.Exec('bpformation.package.List', {'filters': bpformation.args.args.filter }, cols=['name','uuid','owner','visibility','status'])


	def PackageListOS(self):
		self.Exec('bpformation.package.ListOS', {'type': bpformation.args.args.type }, cols=['Name','ID'])


	def PackageExecute(self):
		self.Exec('bpformation.package.Execute', 
		          {'uuid': bpformation.args.args.uuid, 'servers': bpformation.args.args.server, 'parameters': bpformation.args.args.parameter })


	def BlueprintList(self):
		self.Exec('bpformation.blueprint.List', 
		          {'filters': bpformation.args.args.filter, 'accounts': bpformation.args.args.account }, cols=['name','id','visibility','date_added'])


	def BlueprintExport(self):
		self.Exec('bpformation.blueprint.Export', {'id': bpformation.args.args.id, 'file': bpformation.args.args.file }, cols=[])


	def BlueprintImport(self):
		self.Exec('bpformation.blueprint.Import', {'files': bpformation.args.args.file }, cols=[])


	def BlueprintUpdate(self):
		self.Exec('bpformation.blueprint.Update', {'files': bpformation.args.args.file }, cols=[])


	def BlueprintDelete(self):
		self.Exec('bpformation.blueprint.Delete', {'ids': bpformation.args.args.id }, cols=[])


	def BlueprintExecute(self):
		self.Exec('bpformation.blueprint.Execute', 
		          {'files': bpformation.args.args.file, 'type': bpformation.args.args.type, 'password': bpformation.args.args.password,
				   'group_id': bpformation.args.args.group_id, 'network': bpformation.args.args.network, 'dns': bpformation.args.args.dns,
				   'parameters': bpformation.args.args.parameter, 'ids': bpformation.args.args.id })


	def Exec(self,function,args=False,cols=None,supress_output=False):
		try:
			if args:  r = eval("%s(**%s)" % (function,args))
			else:  r = eval("%s()" % (function))

			#  Filter results
			if bpformation.args.args.cols:  cols = bpformation.args.args.cols

			# Output results
			# TODO - how do we differentiate blueprints vs. queue RequestIDs?
			#if r is not None and 'RequestID' in r and not bpformation.args.args.async:  
			#	r = bpformation.output.RequestBlueprintProgress(r['RequestID'],self._GetLocation(),self._GetAlias(),bpformation.args.args.quiet)
			#	cols = ['Server']

			if r and cols and len(cols):
				if not isinstance(r, list):  r = [r]
				if not supress_output and bpformation.args.args.format == 'json':  print bpformation.output.Json(r,cols)
				elif not supress_output and bpformation.args.args.format == 'table':  print bpformation.output.Table(r,cols)
				elif not supress_output and bpformation.args.args.format == 'text':  print bpformation.output.Text(r,cols)
				elif not supress_output and bpformation.args.args.format == 'csv':  print bpformation.output.Csv(r,cols)

			#return(r)
		except KeyboardInterrupt:
			bpformation.output.Status("ERROR",3,"Exiting keyboard interupt")
			sys.exit(1)
		except:
			raise


