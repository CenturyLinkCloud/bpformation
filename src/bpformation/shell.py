"""Command-line interface to the CenturyLink Cloud (CLC) API."""

import argparse
import ConfigParser
import os
import sys

import bpformation


class Args:

	def __init__(self):
		bpformatio.args = self
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
		#  o list (optional filter against metadata)
		#  o package (zip given file manifest or directory.  Gen UUID.  Multiple options based on publish target)
		#  o upload
		#  o publish
		#  o delete
		#  o download
		#
		# TODO vNext:
		#  o dependencies tree
		#

		parser_package = parser_sp1.add_parser('package', help='Package level activities (list, package, upload, publish, etc.)')
		parser_sp2 = parser_account.add_subparsers(dest='sub_command')

		## List unpublished
		parser_account_get = parser_sp2.add_parser('list-unpublished', help='List all upublished packages in specified sub-account')

		## List published
		parser_account_get = parser_sp2.add_parser('list', help='List all available packages Get details on root or specified sub-account')
		parser_account_get.add_argument('--alias', help='Operate on specific account alias')
		#parser_sp9.add_parser('list-system', help='List all system packages of any visibility')
		#parser_sp9.add_parser('list-scripts', help='List all script packages of any visibility')
		#parser_sp9.add_parser('list-software', help='List all software packages of any visibility')



		########## Blueprint ###########
		#
		# TODO vCur:
		#  o list (optional filter against metadata)
		#  o delete
		#  o export (to json)
		#  o import (from json)
		#  o modify
		#
		# TODO vNext:
		#  o create (interactive ui to build blueprint)
		#  o dependencies tree
		#

		#parser_blueprint = parser_sp1.add_parser('blueprint', help='Blueprint level activities (list, import, export, modify, etc.)')
		#parser_sp2 = parser_account.add_subparsers(dest='sub_command')



		########## Global ###########
		#parser.add_argument('--cols', nargs='*', metavar='COL', help='Include only specific columns in the output')
		parser.add_argument('--config', '-c', help='Ini config file')
		parser.add_argument('--alias', '-a', help='Operate on specific account alias')
		parser.add_argument('--control-user', metavar='USER', help='Control username')
		parser.add_argument('--control-password', metavar='PASS', help='Control password')
		parser.add_argument('--quiet', '-q', action='count', help='Supress status output (repeat up to 2 times)')
		parser.add_argument('--verbose', '-v', action='count', help='Increase verbosity')
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
				clc.v1.output.Status('ERROR',3,"Config file %s not found" % (self.args.config))
				sys.exit(1)
		elif os.name=='nt':
			if os.path.isfile("%s/clc/clc.ini" % (os.getenv("PROGRAMDATA"))):
				config_file = "%s/clc/clc.ini" % (os.getenv("PROGRAMDATA"))
			elif os.path.isfile("clc.ini"):
				config_file = "clc.ini"
		else:
			if os.path.isfile("%s/.clc" % (os.environ['HOME'])):
				config_file = "%s/.clc" % (os.environ['HOME'])
			elif os.path.isfile("/usr/local/etc/clc_config"):
				config_file = "/usr/local/etc/clc_config"
		if config_file:  
			clc.v1.output.Status('SUCCESS',3,"Reading %s" % (config_file))
			config = ConfigParser.ConfigParser()
			config.read(config_file)

			if config.has_option('global','v1_api_key'):  clc.v1.V1_API_KEY = config.get('global','v1_api_key')
			if config.has_option('global','v1_api_passwd'):  clc.v1.V1_API_PASSWD = config.get('global','v1_api_passwd')
			if config.has_option('global','v2_api_username'):  clc.v2.V2_API_USERNAME = config.get('global','v2_api_username')
			if config.has_option('global','v2_api_passwd'):  clc.v1.V2_API_PASSWD = config.get('global','v2_api_passwd')

			if config.has_option('global','blueprint_ftp_url'):  clc._BLUEPRINT_FTP_URL = config.get('global','blueprint_ftp_url')


	def MergeEnvironment(self):
		if 'V1_API_KEY' in os.environ:  clc.v1.V1_API_KEY = os.environ['V1_API_KEY']
		if 'V1_API_PASSWD' in os.environ:  clc.v1.V1_API_PASSWD = os.environ['V1_API_PASSWD']
		if 'V2_API_USERNAME' in os.environ:  clc.v2.V2_API_USERNAME = os.environ['V2_API_USERNAME']
		if 'V2_API_PASSWD' in os.environ:  clc.v2.V2_API_PASSWD = os.environ['V2_API_PASSWD']


	def MergeCommands(self):
		if self.args.v1_api_key:  clc.v1.V1_API_KEY = self.args.v1_api_key
		if self.args.v1_api_passwd:  clc.v1.V1_API_PASSWD = self.args.v1_api_passwd
		if self.args.v2_api_username:  clc.v2.V2_API_USERNAME = self.args.v2_api_username
		if self.args.v2_api_passwd:  clc.v2.V2_API_PASSWD = self.args.v2_api_passwd




class ExecCommand():
	def __init__(self):
		import clc.APIv1.output

		try:
			self.Bootstrap()
		except Exception as e:
			clc.v1.output.Status("ERROR",3,"Exiting due to error: %s" % (str(e)))
			sys.exit(1)


	def Bootstrap(self):
		if clc.args.GetCommand() == 'accounts':  self.Account()
		elif clc.args.GetCommand() == 'users':  self.User()
		elif clc.args.GetCommand() == 'groups':  self.Group()
		elif clc.args.GetCommand() == 'servers':  self.Server()
		elif clc.args.GetCommand() == 'billing':  self.Billing()
		elif clc.args.GetCommand() == 'networks':  self.Network()
		elif clc.args.GetCommand() == 'queue':  self.Queue()
		elif clc.args.GetCommand() == 'blueprints':  self.Blueprints()


	def Account(self):
		if clc.args.GetArgs().sub_command == 'list':  self.GetAccounts()
		elif clc.args.GetArgs().sub_command == 'get':  self.GetAccountDetails()
		elif clc.args.GetArgs().sub_command == 'locations':  self.GetLocations()


	def User(self):
		if clc.args.GetArgs().sub_command == 'list':  self.GetUsers()
		elif clc.args.GetArgs().sub_command == 'get':  self.GetUserDetails()
		elif clc.args.GetArgs().sub_command == 'create':  self.CreateUser()
		elif clc.args.GetArgs().sub_command == 'update':  self.UpdateUser()
		elif clc.args.GetArgs().sub_command == 'delete':  self.DeleteUser()
		elif clc.args.GetArgs().sub_command == 'suspend':  self.SuspendUser()
		elif clc.args.GetArgs().sub_command == 'unsuspend':  self.UnsuspendUser()


	def Group(self):
		if clc.args.GetArgs().sub_command == 'list':  self.GetGroups()
		elif clc.args.GetArgs().sub_command == 'create':  self.CreateGroup()
		elif clc.args.GetArgs().sub_command == 'delete':  self.DeleteGroup()
		elif clc.args.GetArgs().sub_command == 'pause':  self.PauseGroup()
		elif clc.args.GetArgs().sub_command == 'archive':  self.ArchiveGroup()
		elif clc.args.GetArgs().sub_command == 'restore':  self.RestoreGroup()
		elif clc.args.GetArgs().sub_command == 'poweron':  self.PoweronGroup()


	def Server(self):
		if clc.args.GetArgs().sub_command == 'list-all':  self.GetAllServers()
		elif clc.args.GetArgs().sub_command == 'list':  self.GetServers()
		elif clc.args.GetArgs().sub_command == 'templates':  self.GetServerTemplates()
		elif clc.args.GetArgs().sub_command == 'get':  self.GetServerDetails()
		elif clc.args.GetArgs().sub_command == 'delete':  self.ServerActions("Delete")
		elif clc.args.GetArgs().sub_command == 'archive':  self.ServerActions("Archive")
		elif clc.args.GetArgs().sub_command == 'poweron':  self.ServerActions("Poweron")
		elif clc.args.GetArgs().sub_command == 'poweroff':  self.ServerActions("Poweroff")
		elif clc.args.GetArgs().sub_command == 'reset':  self.ServerActions("Reset")
		elif clc.args.GetArgs().sub_command == 'shutdown':  self.ServerActions("Shutdown")
		elif clc.args.GetArgs().sub_command == 'snapshot':  self.ServerActions("Snapshot")
		elif clc.args.GetArgs().sub_command == 'pause':  self.ServerActions("Pause")
		elif clc.args.GetArgs().sub_command == 'create':  self.CreateServer()
		elif clc.args.GetArgs().sub_command == 'convert-to-template':  self.ConvertToTemplate()
		elif clc.args.GetArgs().sub_command == 'get-credentials':  self.GetServerCredentials()
		elif clc.args.GetArgs().sub_command == 'list-disks':  self.GetServerDisks()


	def Network(self):
		if clc.args.GetArgs().sub_command == 'list':  self.GetNetworks()
		elif clc.args.GetArgs().sub_command == 'get':  self.GetNetworkDetails()


	def Billing(self):
		if clc.args.GetArgs().sub_command == 'group-estimate':  self.GetGroupEstimate()
		elif clc.args.GetArgs().sub_command == 'group-summaries':  self.GetGroupSummaries()
		elif clc.args.GetArgs().sub_command == 'account-summary':  self.GetAccountSummary()
		elif clc.args.GetArgs().sub_command == 'server-estimate':  self.GetServerEstimate()


	def Queue(self):
		if clc.args.GetArgs().sub_command == 'list':  self.GetQueue()


	def Blueprints(self):
		if clc.args.GetArgs().sub_command == 'list-pending':  self.GetBlueprintsPending()
		elif clc.args.GetArgs().sub_command == 'list':  self.GetBlueprintsPackages()
		elif clc.args.GetArgs().sub_command == 'list-system':  self.GetBlueprintsSystemPackages()
		elif clc.args.GetArgs().sub_command == 'list-scripts':  self.GetBlueprintsScriptsPackages()
		elif clc.args.GetArgs().sub_command == 'list-software':  self.GetBlueprintsSoftwarePackages()
		elif clc.args.GetArgs().sub_command == 'package-upload':  self.GetBlueprintsPackageUpload()
		elif clc.args.GetArgs().sub_command == 'package-publish':  self.PublishBlueprintsPackage()


	def _GetAlias(self):
		if clc.args.args.alias:  return(clc.args.args.alias)
		else:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS

			return(alias)


	def _GetLocation(self):
		location = None
		try:
			location = clc.args.args.location
		except:
			if not location:
				self.Exec('clc.v1.Account.GetLocation','',supress_output=True)
				location = clc.LOCATION

		return(location)


	def GetAccounts(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		self.Exec('clc.v1.Account.GetAccounts', {'alias': alias}, cols=['AccountAlias','ParentAlias','BusinessName','Location','IsActive'])


	def GetAccountDetails(self):
		self.Exec('clc.v1.Account.GetAccountDetails', {'alias': self._GetAlias()}, cols=['AccountAlias', 'Status', 'City', 'Fax', 'Address1', 'Address2', 'ShareParentNetworks', 'Telephone', 'Country', 'Location', 'BusinessName', 'PostalCode', 'TimeZone', 'StateProvince', 'ParentAlias'])


	def GetLocations(self):
		self.Exec('clc.v1.Account.GetLocations', {}, cols=['Alias', 'Region'])


	def GetUsers(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		self.Exec('clc.v1.User.GetUsers', { 'alias': alias }, cols=['UserName','EmailAddress','FirstName','LastName','Roles'])


	def DeleteUser(self):
		self.Exec('clc.v1.User.DeleteUser', { 'user': clc.args.args.user }, supress_output=True)


	def SuspendUser(self):
		self.Exec('clc.v1.User.SuspendUser', { 'user': clc.args.args.user }, supress_output=True)


	def UnsuspendUser(self):
		self.Exec('clc.v1.User.UnsuspendUser', { 'user': clc.args.args.user }, supress_output=True)


	def GetUserDetails(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		self.Exec('clc.v1.User.GetUserDetails', { 'alias': alias, 'user': clc.args.GetArgs().user}, 
		          cols=['UserName', 'MobileNumber', 'AllowSMS', 'SAMLUserName', 'Status', 'Roles', 'FirstName', 'Title', 
				        'LastName', 'OfficeNumber', 'FaxNumber', 'TimeZoneID', 'AccountAlias', 'EmailAddress', 'AlternateEmailAddress'])


	def CreateUser(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		self.Exec('clc.v1.User.CreateUser', { 'alias': alias, 'user': clc.args.args.user, 'email': clc.args.args.email, 
		                                   'first_name': clc.args.args.first_name, 'last_name': clc.args.args.last_name,
										   'roles': clc.args.args.roles }, 
		          cols=['UserName', 'MobileNumber', 'AllowSMS', 'SAMLUserName', 'Status', 'Roles', 'FirstName', 'Title', 
				        'LastName', 'OfficeNumber', 'FaxNumber', 'TimeZoneID', 'AccountAlias', 'EmailAddress', 'AlternateEmailAddress'])


	def UpdateUser(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		self.Exec('clc.v1.User.UpdateUser', { 'alias': alias, 'user': clc.args.args.user, 'email': clc.args.args.email, 
		                                   'first_name': clc.args.args.first_name, 'last_name': clc.args.args.last_name,
										   'roles': clc.args.args.roles }, 
		          cols=['UserName', 'MobileNumber', 'AllowSMS', 'SAMLUserName', 'Status', 'Roles', 'FirstName', 'Title', 
				        'LastName', 'OfficeNumber', 'FaxNumber', 'TimeZoneID', 'AccountAlias', 'EmailAddress', 'AlternateEmailAddress'])


	def GetGroups(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		self.Exec('clc.v1.Group.GetGroups', { 'alias': alias, 'location': location }, cols=['UUID','Name','ParentUUID','IsSystemGroup'])


	def CreateGroup(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		if not clc.args.args.parent:  parent = "%s Hardware" % (location)
		else:  parent = clc.args.args.parent
		self.Exec('clc.v1.Group.Create', 
		          { 'alias': alias, 'location': location, 'parent': parent, 'group': clc.args.args.group, 
				    'description': clc.args.args.description }, 
		          cols=['UUID','Name','ParentUUID'])


	def DeleteGroup(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		self.Exec('clc.v1.Group.Delete', 
		          { 'alias': alias, 'location': location, 'group': clc.args.args.group },
		          cols=['RequestID','StatusCode','Message'])


	def PauseGroup(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		self.Exec('clc.v1.Group.Pause', 
		          { 'alias': alias, 'location': location, 'group': clc.args.args.group },
		          cols=['RequestID','StatusCode','Message'])


	def PoweronGroup(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		self.Exec('clc.v1.Group.Poweron', 
		          { 'alias': alias, 'location': location, 'group': clc.args.args.group },
		          cols=['RequestID','StatusCode','Message'])


	def ArchiveGroup(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetLocation','',supress_output=True)
			location = clc.LOCATION
		self.Exec('clc.v1.Group.Archive', 
		          { 'alias': alias, 'location': location, 'group': clc.args.args.group },
		          cols=['RequestID','StatusCode','Message'])


	def GetServerDetails(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Server.GetServerDetails', { 'alias': alias, 'servers': clc.args.GetArgs().server },
		              cols=['HardwareGroupUUID', 'Name', 'Description', 'Cpu','MemoryGB','Status','TotalDiskSpaceGB','ServerType','OperatingSystem','PowerState','Location','IPAddress'])


	def GetServerCredentials(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Server.GetCredentials', { 'alias': alias, 'servers': clc.args.GetArgs().server },
		              cols=['Username', 'Password', ])


	def GetServerDisks(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Server.GetDisks', { 'alias': alias, 'server': clc.args.GetArgs().server },
		              cols=['Name', 'ScsiBusID', 'ScsiDeviceID', 'SizeGB' ])


	def ServerActions(self,action):
		clc.args.args.async = True  # Force async - we can't current deal with multiple queued objects
		r = self.Exec('clc.v1.Server.%s' % (action), { 'alias': self._GetAlias(), 'servers': clc.args.GetArgs().server },
		              cols=['RequestID','StatusCode','Message'])


	def ConvertToTemplate(self):
		r = self.Exec('clc.v1.Server.ConvertToTemplate', 
		              { 'alias': self._GetAlias(), 'server': clc.args.GetArgs().server, 
					    'template': clc.args.GetArgs().template, 'password': clc.args.GetArgs().password },
		              cols=['RequestID','StatusCode','Message'])


	def GetServers(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		if clc.args.args.location:  location = clc.args.args.location
		else:  
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		r = self.Exec('clc.v1.Server.GetServers', { 'alias': alias, 'location': location, 'group': clc.args.args.group, 'name_groups': clc.args.args.name_groups },
		              cols=['HardwareGroupUUID', 'Name', 'Description', 'Cpu','MemoryGB','Status','ServerType','OperatingSystem','PowerState','Location','IPAddress'])


	def GetServerTemplates(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		if clc.args.args.location:  location = clc.args.args.location
		else:  location = None
		r = self.Exec('clc.v1.Server.GetTemplates', { 'alias': alias, 'location': location }, cols=['OperatingSystem', 'Name', 'Description', 'Cpu','MemoryGB','TotalDiskSpaceGB'])


	def GetAllServers(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.Server.GetAllServers', { 'alias': alias, 'name_groups': clc.args.args.name_groups },
		              cols=['HardwareGroupUUID', 'Name', 'Description', 'Cpu','MemoryGB','Status','ServerType','OperatingSystem','PowerState','Location','IPAddress'])


	def CreateServer(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		r = self.Exec('clc.v1.Server.Create', 
		              { 'alias': alias, 'location': location, 'group': clc.args.args.group, 'name': clc.args.args.name, 'template': clc.args.args.template,
					    'backup_level': clc.args.args.backup_level, 'cpu': clc.args.args.cpu, 'ram': clc.args.args.ram, 
						'network': clc.args.args.network, 'password': clc.args.args.password, 'description': clc.args.args.description, },
		              cols=['RequestID','StatusCode','Message'])


	#def RestoreGroup(self):
	#	alias = None
	#	location = None
	#	if clc.args.args.alias:  alias = clc.args.args.alias
	#	if clc.args.args.location:  location = clc.args.args.location
	#	if not alias:
	#		self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
	#		alias = clc.ALIAS
	#	if not location:
	#		self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
	#		location = clc.LOCATION
	#	self.Exec('clc.Group.Restore', 
	#	          { 'alias': alias, 'location': location, 'group': clc.args.args.group },
	#	          cols=['RequestID','StatusCode','Message'])


	def GetGroupEstimate(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		r = self.Exec('clc.v1.Billing.GetGroupEstimate', { 'alias': alias, 'location': location, 'group': clc.args.GetArgs().group }, 
					  cols=['MonthToDate', 'PreviousHour', 'MonthlyEstimate', 'CurrentHour'])


	def GetGroupSummaries(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Billing.GetGroupSummaries', { 'alias': alias, 'date_start': clc.args.GetArgs().date_start, 'date_end': clc.args.GetArgs().date_end },
		              cols=['GroupName', 'LocationAlias', 'MonthlyEstimate', 'MonthToDate',  'CurrentHour'])


	def GetServerEstimate(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Billing.GetServerEstimate', { 'alias': alias, 'server': clc.args.GetArgs().server },
		              cols=['MonthToDate', 'PreviousHour', 'MonthlyEstimate', 'CurrentHour'])


	def GetAccountSummary(self):
		if clc.args.args.alias:  alias = clc.args.args.alias
		else:  alias = None
		r = self.Exec('clc.v1.Billing.GetAccountSummary', { 'alias': alias }, cols=['OneTimeCharges','MonthToDate', 'MonthlyEstimate', 'CurrentHour', 'PreviousHour'])


	def GetNetworks(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		r = self.Exec('clc.v1.Network.GetNetworks', { 'alias': alias, 'location': location }, 
					  cols=['Name', 'Description', 'Gateway'])


	def GetNetworkDetails(self):
		alias = None
		location = None
		if clc.args.args.alias:  alias = clc.args.args.alias
		if clc.args.args.location:  location = clc.args.args.location
		if not alias:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			alias = clc.ALIAS
		if not location:
			self.Exec('clc.v1.Account.GetAlias','',supress_output=True)
			location = clc.LOCATION
		r = self.Exec('clc.v1.Network.GetNetworkDetails', { 'alias': alias, 'location': location, 'network': clc.args.args.network }, 
					  cols=['Address', 'AddressType', 'IsClaimed', 'ServerName'])


	def GetQueue(self):
		r = self.Exec('clc.v1.Queue.List', { 'type': clc.args.args.type }, cols=['RequestID', 'RequestTitle', 'ProgressDesc', 'CurrentStatus', 'StepNumber', 'PercentComplete'])


	def GetBlueprintsPending(self):
		r = self.Exec('clc.v1.Blueprint.GetPendingPackages', { }, cols=['Name'])


	def GetBlueprintsPackages(self):
		r = self.Exec('clc.v1.Blueprint.GetPackages', { 'classification': clc.args.args.type, 'visibility': clc.args.args.visibility }, 
		              cols=['ID','Name'])


	def GetBlueprintsSystemPackages(self):
		r = self.Exec('clc.v1.Blueprint.GetAllSystemPackages', { }, cols=['ID','Name','Visibility'])


	def GetBlueprintsScriptsPackages(self):
		r = self.Exec('clc.v1.Blueprint.GetAllScriptsPackages', { }, cols=['ID','Name','Visibility'])


	def GetBlueprintsSoftwarePackages(self):
		r = self.Exec('clc.v1.Blueprint.GetAllSoftwarePackages', { }, cols=['ID','Name','Visibility'])


	def GetBlueprintsPackageUpload(self):
		if clc.args.args.ftp:  ftp_url = clc.args.args.ftp
		elif clc._BLUEPRINT_FTP_URL:  ftp_url = clc._BLUEPRINT_FTP_URL
			
		try:
			r = self.Exec('clc.v1.Blueprint.PackageUpload', { 'package': clc.args.args.package, 'ftp_url': ftp_url },supress_output=True)
		except UnboundLocalError:
			clc.v1.output.Status('ERROR',2,'FTP URL not defined.  Use --ftp command line arg or set blueprint_ftp_url in ini file')


	def PublishBlueprintsPackage(self):
		clc.args.args.async = True
		if clc.args.args.os is None:
			r = self.Exec('clc.v1.Blueprint.PackagePublishUI', 
			              { 'package': clc.args.args.package, 'classification': clc.args.args.type, 'visibility': clc.args.args.visibility },
						  cols=['RequestID','StatusCode','Message'])
		else:
			r = self.Exec('clc.v1.Blueprint.PackagePublish', 
			              { 'package': clc.args.args.package, 'classification': clc.args.args.type, 'os': clc.args.args.os, 'visibility': clc.args.args.visibility },
						  cols=['RequestID','StatusCode','Message'])


	def Exec(self,function,args=False,cols=None,supress_output=False):
		try:
			if args:  r = eval("%s(**%s)" % (function,args))
			else:  r = eval("%s()" % (function))

			#  Filter results
			if clc.args.args.cols:  cols = clc.args.args.cols

			# Output results
			# TODO - how do we differentiate blueprints vs. queue RequestIDs?
			if r is not None and 'RequestID' in r and not clc.args.args.async:  
				r = clc.v1.output.RequestBlueprintProgress(r['RequestID'],self._GetLocation(),self._GetAlias(),clc.args.args.quiet)
				cols = ['Server']

			if not isinstance(r, list):  r = [r]
			if not supress_output and clc.args.args.format == 'json':  print clc.v1.output.Json(r,cols)
			elif not supress_output and clc.args.args.format == 'table':  print clc.v1.output.Table(r,cols)
			elif not supress_output and clc.args.args.format == 'text':  print clc.v1.output.Text(r,cols)
			elif not supress_output and clc.args.args.format == 'csv':  print clc.v1.output.Csv(r,cols)

			return(r)
		except clc.AccountDeletedException:
			clc.v1.output.Status('ERROR',2,'Unable to process, account in deleted state')
		except clc.AccountLoginException:
			clc.v1.output.Status('ERROR',2,'Transient login error.  Please retry')


