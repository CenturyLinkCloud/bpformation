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
		parser = argparse.ArgumentParser(description="CLI tool for interacting with CenturyLink Blueprints Package and Workflow Services.  http://www.CenturyLinkCloud.com")
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



		########## Blueprint ###########
		#
		# TODO vCur:
		#  o import (from json)
		#  o modify
		#  o delete
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

		## Export
		parser_blueprint_export = parser_sp2.add_parser('export', help='Export blueprint')
		parser_blueprint_export.add_argument('--id', required=True, help='Blueprint ID (note this ID is not globally unique - find this from your primary datacenter')
		parser_blueprint_export.add_argument('--file', required=False, help='Filename target for Blueprint json definition')

		## Import
		parser_blueprint_export = parser_sp2.add_parser('import', help='Import blueprint from json')
		parser_blueprint_export.add_argument('--file', nargs='*', required=True, help='Blueprint definition json files')

		## Delete
		parser_blueprint_export = parser_sp2.add_parser('delete', help='Delete blueprint')
		parser_blueprint_export.add_argument('--id', required=True, help='Blueprint ID (note this ID is not globally unique - find this from your primary datacenter')



		########## Global ###########
		#parser.add_argument('--cols', nargs='*', metavar='COL', help='Include only specific columns in the output')
		parser.add_argument('--config', '-c', help='Ini config file')
		parser.add_argument('--alias', '-a', help='Operate on specific account alias')
		parser.add_argument('--control-user', metavar='USER', help='Control username')
		parser.add_argument('--control-password', metavar='PASS', help='Control password')
		parser.add_argument('--quiet', '-q', action='count', help='Supress status output (repeat up to 2 times)')
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
			bpformation.output.Status('SUCCESS',3,"Reading %s" % (config_file))
			config = ConfigParser.ConfigParser()
			config.read(config_file)

			if config.has_option('global','control_user'):  bpformation.CONTROL_USER = config.get('global','control_user')
			if config.has_option('global','control_password'):  bpformation.CONTROL_PASSWORD = config.get('global','control_password')


	def MergeEnvironment(self):
		if 'CONTROL_USER' in os.environ:  bpformation.CONTROL_USER = os.environ['CONTROL_USER']
		if 'CONTROL_PASSWORD' in os.environ:  bpformation.CONTROL_PASSWORD = os.environ['CONTROL_PASSWORD']


	def MergeCommands(self):
		if self.args.control_user:  bpformation.CONTROL_USER = self.args.control_user
		if self.args.control_password:  bpformation.CONTROL_PASSWORD = self.args.control_password




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
		elif bpformation.args.GetArgs().sub_command == 'publish':  self.PackagePublish()
		elif bpformation.args.GetArgs().sub_command == 'upload-and-publish':  self.PackageUploadAndPublish()
		elif bpformation.args.GetArgs().sub_command == 'delete':  self.PackageDelete()
		elif bpformation.args.GetArgs().sub_command == 'download':  self.PackageDownload()
		elif bpformation.args.GetArgs().sub_command == 'list':  self.PackageList()


	def Blueprint(self):
		if bpformation.args.GetArgs().sub_command == 'list':  self.BlueprintList()
		elif bpformation.args.GetArgs().sub_command == 'export':  self.BlueprintExport()
		elif bpformation.args.GetArgs().sub_command == 'delete':  self.BlueprintDelete()
		elif bpformation.args.GetArgs().sub_command == 'import':  self.BlueprintImport()


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


	def BlueprintList(self):
		self.Exec('bpformation.blueprint.List', {'filters': bpformation.args.args.filter }, cols=['name','id','owner','visibility','date_added'])


	def BlueprintExport(self):
		self.Exec('bpformation.blueprint.Export', {'id': bpformation.args.args.id, 'file': bpformation.args.args.file }, cols=[])


	def BlueprintImport(self):
		self.Exec('bpformation.blueprint.Import', {'files': bpformation.args.args.file }, cols=[])


	def BlueprintDelete(self):
		self.Exec('bpformation.blueprint.Delete', {'id': bpformation.args.args.id }, cols=[])


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

			if r and len(cols):
				if not isinstance(r, list):  r = [r]
				if not supress_output and bpformation.args.args.format == 'json':  print bpformation.output.Json(r,cols)
				elif not supress_output and bpformation.args.args.format == 'table':  print bpformation.output.Table(r,cols)
				elif not supress_output and bpformation.args.args.format == 'text':  print bpformation.output.Text(r,cols)
				elif not supress_output and bpformation.args.args.format == 'csv':  print bpformation.output.Csv(r,cols)

			#return(r)
		except:
			raise


