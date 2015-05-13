# -*- coding: utf-8 -*-
"""
CenturyLink Cloud Python Blueprint Package and Workflow CLI management tool.

CenturyLink Cloud: http://www.CenturyLinkCloud.com
Package Github page: https://github.com/CenturyLinkCloud/bp-formation

"""

import Package as package
import Blueprint as blueprint
import Web as web
import Output as output
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

