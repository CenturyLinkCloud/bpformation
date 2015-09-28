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
from bpformation.api import API as api
from bpformation.queue import Queue as queue
import bpformation.output
import defaults


####### module/object vars #######
CONTROL_USER = False
CONTROL_PASSWORD = False
ALIAS = False
FTP_ENDPOINT = False


__version__ = "0.21"

args = False
config = False

_SSL_VERIFY = True

_ALIAS = False
_LOGINS = 0
_CONTROL_COOKIES = False
_BLUEPRINT_FTP_URL = False
_bearer_token = False

class BPFormationExeption(Exception):
	pass
class BPFormationFatalExeption(Exception):
	pass
class BPFormationLoginException(BPFormationExeption):
	pass

