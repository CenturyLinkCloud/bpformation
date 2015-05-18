# -*- coding: utf-8 -*-
"""
Manage Blueprint workflows.
"""

import re
import sys
import time

import bpformation



class Queue():

	@staticmethod
	def WaitForQueue(queues):
		# Param is list of work queue hrefs - these include the work queue ID and the in-scope datacenter

		for queue in queues:
			while True:
				r = bpformation.web.CallScrape("GET",
				                               "/blueprints/queue/BlueprintProgress/?requestID=%s&location=%s&ts=%s" % 
											   		(queue['id'],queue['location'],int(time.time()))).text
				if re.search('<input id="blueprint-percent-complete" name="blueprint-percent-complete" type="hidden" value="100" /',r):
					if 'date_added' in queue: 
						bpformation.output.Status('SUCCESS',3,"%s publish job complete (%s seconds)" % (queue['description'],int(time.time()-queue['date_added'])))
					else:  
						bpformation.output.Status('SUCCESS',3,"%s publish job complete" % queue['description'])
					break
				else:  time.sleep(1)


