# -*- coding: utf-8 -*-
"""
Manage Blueprint workflows.
"""

import re
import sys

import bpformation



class Queue():

	@staticmethod
	def WaitForQueue(hrefs):
		# Param is list of work queue hrefs - these include the work queue ID and the in-scope datacenter

		for href in hrefs:
			r = bpformation.web.CallScrape("GET",href
		# TODO foreach item wait for terminal status
		# Once all items are terminal output status


