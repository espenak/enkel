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

""" Defines a basic standalone WSGI server/handler.

WSGI is specified in PEP 333 which can be found
U{here <http://www.python.org/dev/peps/pep-0333>}.
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn, ForkingMixIn
from os import environ
from datetime import datetime
from sys import stderr
import logging

from server_base import WsgiServerMixIn, LoggerAsErrorFile
from apprunner import run_app, Response
from utils import rfc1123_date
from env import urlpath_to_environ


class HttpServerResponse(Response):
	""" Adds automatic adding of required http headers
	to the L{apprunner.Response} class. Headers are only added
	when not supplied by the app. These headers are handled:
		- server (defaults to L{__init__} parameter I{server_info})
		- date (defaults to the UTC/GMT time when the response is sent)
	"""
	def __init__(self, server_info, *args, **kw):
		super(HttpServerResponse, self).__init__(*args, **kw)
		self.server_info = server_info

	def validate_header(self, name, value):
		if name in ("server", "date"):
			try:
				del self.extra_headers[name]
			except KeyError:
				pass

	def generate_headers(self):
		self.extra_headers["server"] = self.server_info
		self.extra_headers["date"] = rfc1123_date(datetime.utcnow())
		return super(HttpServerResponse, self).generate_headers()



class WsgiRequestHandler(BaseHTTPRequestHandler):
	""" A WSGI request handler. You do not call this directly,
	but send it as a parameter to L{Server.__init__}.

	@cvar ENV: Default values for the WSGI environ dict. See
			L{create_env} for more information.
	"""

	ENV = {}

	def do_GET(self):
		self.handle_wsgi_request("GET")
	def do_POST(self):
		self.handle_wsgi_request("POST")
	def do_OPTIONS(self):
		self.handle_wsgi_request("OPTIONS")
	def do_HEAD(self):
		self.handle_wsgi_request("HEAD")
	def do_PUT(self):
		self.handle_wsgi_request("PUT")
	def do_DELETE(self):
		self.handle_wsgi_request("DELETE")
	def do_TRACE(self):
		self.handle_wsgi_request("TRACE")
	def do_CONNECT(self):
		self.handle_wsgi_request("CONNECT")


	def create_env(self, method):
		""" Create the WSGI environ dict.

		These variables are defined:
			- byte strings:
				- REQUEST_METHOD
				- SERVER_PROTOCOL
				- SERVER_NAME
				- SERVER_PORT
				- CONTENT_TYPE
				- CONTENT_LENGTH
				- REMOTE_ADDR
				- wsgi.url_scheme
			- wsgi.version
			- wsgi.input       (file-like object)
			- wsgi.errors      (file-like object)
			- wsgi.multithread (bool)
			- wsgi.run_once    (bool)
		And all HTTP-headers provided by the client prefixed with
		'HTTP_'.

		@note: This is the most minimal environment allowed by
			PEP 333. You might wish to subclass this to provide
			more environment variables.

		@return: The WSGI environ dict to be sent to the application.
		"""
		env = self.ENV.copy()


		if not (len(self.server.server_address) == 2 and \
				isinstance(self.server.server_address[1], int)):
			raise ValueError("can only listen to internet protocol "\
				"server_address'es, like ('localhost', 8000).")

		env.update({
			"REQUEST_METHOD": method,
			"SERVER_PROTOCOL": self.protocol_version,
			"SERVER_NAME": self.server.server_address[0],
			"SERVER_PORT": str(self.server.server_address[1]),
			"CONTENT_TYPE": self.headers.get("content-type", ""),
			"CONTENT_LENGTH": self.headers.get("content-length", ""),
			"REMOTE_ADDR": self.client_address[0],
			"wsgi.input": self.rfile
		})
		self.server.add_common_wsgienv(env)

		# Add all http headers client provided
		for name in self.headers:
			value = self.headers.get(name)
			env["HTTP_" + name.upper()] = value

		return env


	def handle_wsgi_request(self, method):
		""" Create a WSGI environ dict (using L{create_env} and run
		the app. """

		# Create the WSGI environ dict
		env = self.create_env(method)
		self.server.log.info("connected by %s" % str(self.client_address))

		# parse path
		urlpath_to_environ(env, self.path)

		req = HttpServerResponse(self.server.server_info, self.wfile, env,
				self.server.debug)
		run_app(self.server.app, req)





class Server(HTTPServer, WsgiServerMixIn):
	""" A synchronous HTTP WSGI server.

	Works more or less like L{scgi.Server} which is
	much better documented.
	"""
	REQUEST_HANDLER = WsgiRequestHandler
	url_scheme = "http"
	log = logging.getLogger("enkel.wansgli.http.server")
	applog = LoggerAsErrorFile(logging.getLogger(
		"enkel.wansgli.http.app"))

	def __init__(self, app, server_address=("",9000)):
		"""
		@param app: A WSGI app as defined in PEP 333.
		"""
		self.app = app
		HTTPServer.__init__(self, server_address, self.REQUEST_HANDLER)

class ThreadingServer(ThreadingMixIn, Server):
	""" A threading HTTP WSGI server. """
	MULTITHREAD = True

class ForkingServer(ForkingMixIn, Server):
	""" A forking HTTP WSGI server. """
	MULTIPROCESS = True
