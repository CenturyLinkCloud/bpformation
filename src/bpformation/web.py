# -*- coding: utf-8 -*-
"""Private class that executes Web calls calls."""

import os
import re
import sys
import requests
import xml.etree.ElementTree

import bpformation

#
# TODO vCur:
#  o Set alias
#

#
# TODO vNext:
#


class Web():
	
	# requests module includes cacert.pem which is visible when run as installed module.
	# pyinstall single-file deployment needs cacert.pem packaged along and referenced.
	# This module proxies between the two based on whether the cacert.pem exists in
	# the expected runtime directory.
	#
	# https://github.com/kennethreitz/requests/issues/557
	# http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
	#
	@staticmethod
	def _ResourcePath(relative):
		if not bpformation._SSL_VERIFY:  return(bpformation._SSL_VERIFY)
		elif os.path.isfile(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")),relative)):
			# Pyinstall packaged windows file
			return(os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")),relative))
		else:
			return(True)


	@staticmethod
	def DisableSSLVerify():
		""" Disable SSL endpoint verification.
		
		 This also disable certification error warnings within log messages with scope extended
		 to all usages of the requests module."""

		try:
			requests.packages.urllib3.disable_warnings()
		except:
			pass


	@staticmethod
	def _DebugRequest(request,response):
		print "\n".join([
			'-----------REQUEST-----------',
			request.method + ' ' + request.url,
			"\n".join([ '%s: %s' % (k, v) for k, v in request.headers.items()]),
			request.body,
		])

		print "\n".join([
			'-----------RESPONSE-----------',
			'status: ' + str(response.status_code),
			response.text
		])


	@staticmethod
	def _LoginScrape():
		"""Login to retrieve bearer token and set default account and location aliases."""
		if not bpformation.CONTROL_USER or not bpformation.CONTROL_PASSWORD:
			bpformation.output.Status('ERROR',3,'Control username and password not provided')
			raise(bpformation.BPFormationLoginException)
			
		r = requests.post("https://control.ctl.io/auth/Login", 
						  allow_redirects=False,
						  verify=Web._ResourcePath('bpformation/cacert.pem'),
						  data={"UserName": bpformation.CONTROL_USER, "Password": bpformation.CONTROL_PASSWORD})
		bpformation._CONTROL_COOKIES = r.cookies

		if r.status_code>=200 and r.status_code<400:
			# TODO - capture and assign alias.
			#bpformation/ALIAS = r.json()['accountAlias']
			bpformation.output.Status('SUCCESS',1,'Logged into control portal')
		elif r.status_code == 400:
			raise(Exception("Invalid V2 API login.  %s" % (r.json()['message'])))
		else:
			raise(Exception("Error logging into V2 API.  Response code %s. message %s" % (r.status_code,r.json()['message'])))


	@staticmethod
	def _SetAliasScrape(alias):
		Web.CallScrape("POST","/Impersonation/Account",{'impersonatedAccount': alias},allow_redirects=False)
		bpformation._ALIAS = alias
		bpformation.output.Status('SUCCESS',1,'Alias set to %s' % bpformation._ALIAS)


	@staticmethod
	def Alias(alias=None):
		if alias:  Web._SetAliasScrape(alias)
		if bpformation._ALIAS == False:
			bpformation._ALIAS = re.search("<title>\s+Account\s+([^\s]+)\s*</title>",Web.CallScrape("GET","/Organization/account/details").text).group(1)
			bpformation.output.Status('SUCCESS',1,'Alias set to %s' % bpformation._ALIAS)

		return(bpformation._ALIAS)


	@staticmethod
	def CallScrape(method,url,payload={},headers=None,allow_redirects=True,debug=False):
		"""Execute screen scrape call

		:param url: URL paths associated with the API call
		:param payload: dict containing all parameters to submit with POST call

		:returns: decoded API json result
		"""
		if not bpformation._CONTROL_COOKIES:  
			Web._LoginScrape()
			if bpformation.ALIAS:  Web.Alias(bpformation.ALIAS)

		fq_url = "%s%s" % (bpformation.defaults.CONTROL_URL,url)

		#if isinstance(payload, basestring):  headers['content-type'] = "Application/json" # added for server ops with str payload
		#headers = None	# Placeholder for future use

		if method=="GET":
			r = requests.request(method,fq_url,
								 headers=headers,
						  		 allow_redirects=allow_redirects,
								 cookies=bpformation._CONTROL_COOKIES,
								 params=payload, 
								 verify=Web._ResourcePath('bpformation/cacert.pem'))
		else:
			r = requests.request(method,fq_url,
								 headers=headers,
						  		 allow_redirects=allow_redirects,
								 cookies=bpformation._CONTROL_COOKIES,
								 data=payload, 
								 verify=Web._ResourcePath('bpformation/cacert.pem'))

		if debug:  
			Web._DebugRequest(request=requests.Request(method,fq_url,data=payload,headers=headers).prepare(),
							  response=r)

		return(r)


	@staticmethod
	def BearerToken():
		"""Return bearer token associated with the current session

		:returns: bearer token
		"""
		if not bpformation._CONTROL_COOKIES:  
			Web._LoginScrape()

		# Ping - validate if we need to login
		try:
			r = bpformation.web.CallScrape("GET","/")
			if not re.search("<title> Control Portal Dashboard </title>",r.text):
				raise(bpformation.BPFormationLoginException)
		except requests.exceptions.ConnectionError:
			raise
			raise(bpformation.BPFormationLoginException)
		
		# Extract token
		m = re.search("""shell.user.set\(\{"token":"(.+?)","userName":"(.+?)"\}\);""",r.text)
		username = m.group(2)
		token = m.group(1)

		return(token)


