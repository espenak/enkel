# This file is part of the Enkel web programming library.
#
# Copyright (C) 2007 Espen Angell Kristiansen (espen@wsgi.net)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

""" Error handling middleware. """

from BaseHTTPServer import BaseHTTPRequestHandler
import logging

from enkel.error import EnkelUserError, EnkelFatal, EnkelWarning
from enkel.error.http import HttpUserError



def handle_http_user_error(env, start_response):
	e = env["wsgiorg.routing_args"][0][0]
	status = "%d %s" % (e.NUMBER,
			BaseHTTPRequestHandler.responses[e.NUMBER])
	start_response(status, [("content-type", "text/html")])
	yield "<html><body><h1>%(short_message)s</h1>"\
			"%(long_message)s</body></html>" % e.__dict__

def handle_user_error(env, start_response):
	e = env["wsgiorg.routing_args"][0][0]
	status = "500 error"
	start_response(status, [("content-type", "text/html")])
	yield "<html><body><h1>%(short_message)s</h1>"\
			"%(long_message)s</body></html>" % e.__dict__


def handle_other_error(env, start_response):
	start_response("500 error", [("content-type", "text/plain")])
	return ["Internal server error"]


class ErrorHandler(object):
	""" A WSGI middleware for handling errors.
	It traps errors and forwards them to another WSGI app.
	Before forwarding, the exception is added to the WSGI environ
	dict like this: environ["wsgiorg.routing_args"] = ([exception], {}).

	Example error handler
	=====================
		>>> from enkel.wsgiapp import WsgiApp
		>>> class MyErrorHandler(WsgiApp)
		... 	def run_app(self, exception):
		... 		return str(exception)
	"""
	def __init__(self, app, use_log=True,
			http_error = handle_http_user_error,
			user_error = handle_user_error,
			other_error = handle_other_error):
		"""
		@param use_log: If True, log errors using the logging module.
				HttpUserError and EnkelUserError are sent to
				logging.debug and other exceptions are sent to
				logging.error. exc_info=True is used in all 3 cases.
		@param http_error: A wsgi app that handels any
				L{enkel.error.http.HttpUserError} that is raised.
		@param user_error: A wsgi app that handels any
				L{enkel.error.EnkelUserError} that is raised.
		@param other_error: A wsgi app that handels any error except
				HttpUserError and EnkelUserError.
		"""
		self.app = app
		self.use_log = use_log
		self.handle_user_error = user_error
		self.handle_http_error = http_error
		self.handle_other_error = other_error

	def __call__(self, env, start_response):
		try:
			return self.app(env, start_response)
		except HttpUserError, e:
			if self.use_log:
				logging.debug(str(e), exc_info=True)
			env["wsgiorg.routing_args"] = ([e], {})
			return self.handle_http_error(env, start_response)
		except EnkelUserError, e:
			if self.use_log:
				logging.debug(str(e), exc_info=True)
			env["wsgiorg.routing_args"] = ([e], {})
			return self.handle_user_error(env, start_response)
		except Exception, e:
			if self.use_log:
				logging.error(str(e), exc_info=True)
			env["wsgiorg.routing_args"] = ([e], {})
			return self.handle_other_error(env, start_response)
