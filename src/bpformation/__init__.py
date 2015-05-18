# -*- coding: utf-8 -*-
"""
CenturyLink Cloud Python Blueprint Package and Workflow CLI management tool.

CenturyLink Cloud: http://www.CenturyLinkCloud.com
Package Github page: https://github.com/CenturyLinkCloud/bp-formation

"""

from bpformation.shell import Args, ExecCommand
from bpformation.package import Package as package
from bpformation.blueprint import Blueprint as blueprint
from bpformation.web import Web as web
import bpformation.output
import defaults


####### module/object vars #######
CONTROL_USER = False
CONTROL_PASSWORD = False
ALIAS = False


args = False

_SSL_VERIFY = True

_LOGINS = 0
_BLUEPRINT_FTP_URL = False

class BPFormationExeption(Exception):
	pass
class BPFormationLoginException(BPFormationExeption):
	pass

