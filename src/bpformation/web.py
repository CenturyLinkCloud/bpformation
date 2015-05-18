# -*- coding: utf-8 -*-
"""Private class that executes Web calls calls."""

import os
import sys
import requests
import xml.etree.ElementTree

import bpformation


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
		if not clc._SSL_VERIFY:  return(clc._SSL_VERIFY)
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

		clc._SSL_VERIFY = False
		try:
			requests.packages.urllib3.disable_warnings()
		except:
			pass


	@staticmethod
	def _DebugRequest(request,response):
		print('{}\n{}\n{}\n\n{}\n'.format(
			'-----------REQUEST-----------',
			request.method + ' ' + request.url,
			'\n'.join('{}: {}'.format(k, v) for k, v in request.headers.items()),
			request.body,
		))

		print('{}\n{}\n\n{}'.format(
			'-----------RESPONSE-----------',
			'status: ' + str(response.status_code),
			response.text
		))


	@staticmethod
	def _Login():
		"""Login to retrieve bearer token and set default account and location aliases."""
		if not bpformation.CONTROL_USER or not bpformation.CONTROL_PASSWORD:
			bformation.output.Status('ERROR',3,'Control username and password not provided')
			raise(bpformation.BPFormationLoginException)
			
		r = requests.post("https://control.ctl.io/auth/Login", 
						  allow_redirects=False,
						  verify=Web._ResourcePath('bpformation/cacert.pem'),
						  data={"UserName": bpformation.CONTROL_USER, "Password": bpformation.CONTROL_PASSWORD})
		bpformation._control_cookies = r.cookies

		if r.status_code == 200:
			# TODO - capture and assign alias.
			#clc.ALIAS = r.json()['accountAlias']
			clc.v1.output.Status('SUCCESS',1,'Logged into v1 API')
		elif r.status_code == 400:
			raise(Exception("Invalid V2 API login.  %s" % (r.json()['message'])))
		else:
			raise(Exception("Error logging into V2 API.  Response code %s. message %s" % (r.status_code,r.json()['message'])))


	# TODO
	@staticmethod
	def Alias(alias):
		# TODO
		pass


	# TODO
	@staticmethod
	def Call(method,url,payload={},debug=False):
		"""Execute v2 API call.

		:param url: URL paths associated with the API call
		:param payload: dict containing all parameters to submit with POST call

		:returns: decoded API json result
		"""
		if not clc._LOGIN_TOKEN_V2:  API._Login()

		# If executing refs provided in API they are abs paths,
		# Else refs we build in the sdk are relative
		if url[0]=='/':  fq_url = "%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)
		else:  fq_url = "%s/v2/%s" % (clc.defaults.ENDPOINT_URL_V2,url)

		headers = {'Authorization': "Bearer %s" % clc._LOGIN_TOKEN_V2}
		if isinstance(payload, basestring):  headers['content-type'] = "Application/json" # added for server ops with str payload

		if method=="GET":
			r = requests.request(method,fq_url,
								 headers=headers,
			                     params=payload, 
								 verify=API._ResourcePath('clc/cacert.pem'))
		else:
			r = requests.request(method,fq_url,
								 headers=headers,
			                     data=payload, 
								 verify=API._ResourcePath('clc/cacert.pem'))

		if debug:  
			API._DebugRequest(request=requests.Request(method,fq_url,data=payload,headers=headers).prepare(),
			                  response=r)

		if r.status_code>=200 and r.status_code<300:
			try:
				return(r.json())
			except:
				return({})
		else:
			try:
				e = clc.APIFailedResponse("Response code %s.  %s %s %s" % 
				                          (r.status_code,r.json()['message'],method,"%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)))
				e.response_status_code = r.status_code
				e.response_json = r.json()
				e.response_text = r.text
				raise(e)
			except clc.APIFailedResponse:
				raise
			except:
				e = clc.APIFailedResponse("Response code %s. %s. %s %s" % 
				                         (r.status_code,r.text,method,"%s%s" % (clc.defaults.ENDPOINT_URL_V2,url)))
				e.response_status_code = r.status_code
				e.response_json = {}	# or should this be None?
				e.response_text = r.text
				raise(e)


