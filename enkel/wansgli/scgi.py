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


""" Defines a SCGI WSGI server. """


from SocketServer import StreamRequestHandler, TCPServer, \
	ThreadingMixIn, ForkingMixIn
from re import compile
import logging

from apprunner import run_app, Response
from server_base import WsgiServerMixIn, CGI_ENV_NAMES, \
		check_required_headers, LoggerAsErrorFile


class ScgiRequestHandler(StreamRequestHandler):
	""" A scgi request handler.
	You do not normally use this directly, but rather as a
	REQUEST_HANDLER for the L{Server} class.
	"""

	HEADPATT = compile("([^\0]+)\0([^\0]+)\0")

	@classmethod
	def parse_scgi_headers(cls, stream):
		"""	Parse SCGI input headers into a WSGI environ dict.
		@raise ValueError: If 'headers' is not correctly structured.
		@param stream: The input stream from a SCGI client.
		@return: A WSGI environ dict. You might want to use
				L{server_base.check_required_headers} to make sure
				all the headers required by PEP 333 was recieved from
				the client.
		"""

		length = ""
		c = stream.read(1)
		while c != ":":
			if not c.isdigit():
				raise ValueError(
					"Netstring <length> contains non-digits.")
			length += c
			c = stream.read(1)
			if len(length) > 4:
				raise ValueError(
					"Netstring <length> is more than 9999 byte.")

		try:
			length = int(length)
		except ValueError:
			raise ValueError(
				"Netstring length is not an int.")

		headers = stream.read(length)
		comma = stream.read(1)
		if comma != ",":
			raise ValueError(
				"The first character after the <string> in the "\
				"netstring is not ','")

		env = {
			"SCRIPT_NAME": "",
			"PATH_INFO": "",
		}

		scgi = False
		for match in cls.HEADPATT.finditer(headers):
			name = match.group(1)
			if name in CGI_ENV_NAMES or \
					name.startswith("HTTP_"):
				env[name] = match.group(2)
			elif name == "SCGI":
				scgi = True
		if not scgi:
			raise ValueError(
				"Client did not send the SCGI header. "\
				"Are you sure the client is a SCGI client?")
		return env

	def handle(self):
		self.server.log.info("connected by %s" % str(self.client_address))

		try:
			env = self.__class__.parse_scgi_headers(self.rfile)
			self.server.log.debug(str(env))
			check_required_headers(env)
		except ValueError, e:
			self.server.log.error("%s: %s" % (self.client_address, e))
		else:
			env["wsgi.input"] = self.rfile
			self.server.add_common_wsgienv(env)

			# SCGI servers normally add the Date and Server headers, so we
			# do not need to use a Response that adds them.
			res = Response(self.wfile, env,
					debug = self.server.debug)
			try:
				run_app(self.server.app, res)
			except:
				self.server.log.exception(
					"Uncaught exception in wsgi app.")
		self.request.close()


class Server(TCPServer, WsgiServerMixIn):
	""" A synchronous SCGI WSGI server.

	Usage
	=====
		>>> def myapp(env, start_response):
		... 	start_response("200 ok", [("content-type", "text/plain")])
		... 	yield "hello world"


		A simple example
		----------------

		>>> s = Server(myapp)
		>>> s.serve_forever()


		Tweaking the logging
		--------------------

		Information from the server is handled by the logger module.
		You can override this by setting "log" and "applog" as
		described below in the "Customization" section, but in most
		cases tweaking the logger is better.

		>>> import logger
		>>> logger.basicConfig(level=logging.INFO)
		>>> s.serve_forever()


		Customizing
		-----------

		You can customize the server by subclassing Server
		and by setting some object variables. Let us create a
		multi-threading server.

		>>> from SocketServer import ThreadingMixIn
		>>> class MyServer(ThreadingMixIn, Server):
		... 	MULTITHREAD = True

		Next we will make it listen to 127.0.0.1:8000 and
		it identify itself as "MY server". We use custom
		logging. App errors goes to sys.stderr. Server errors
		goes to a logger named "my.server".

		>>> import sys
		>>> import logging 
		>>> s = MyServer(app, ("127.0.0.1", 8000))
		>>> s.server_info =  "MY server"
		>>> s.applog = sys.stderr
		>>> s.log = logger.getLogger("my.server")
		>>> s.serve_forever()

		Customization is documented in L{server_base.WsgiServerMixIn}.


	Binding to a socket
	===================
		To bind a server to a unix-socket instead of a host+port,
		we must specify that we wish to use unix-sockets, and
		give it a file to bind to.

		>>> from socket import AF_UNIX
		>>> class USserver(Server):
		... 	address_family = AF_UNIX
		>>> s = USserver(myapp, "/var/tmp/mysock")
		>>> s.serve_forever()


	@ivar url_scheme: The url-scheme used on the SCGI client. Should
		be 'http' for plain-text transfers and 'https' for SSL.
		Defaults to 'http'.
	"""
	url_scheme = "http"
	log = logging.getLogger("enkel.wansgli.scgi.server")
	applog = LoggerAsErrorFile(logging.getLogger(
		"enkel.wansgli.scgi.app"))
	REQUEST_HANDLER = ScgiRequestHandler

	def __init__(self, app, server_address=("",9001)):
		"""
		@param app: A WSGI app as defined in PEP 333.
		"""
		self.app = app
		TCPServer.__init__(self, server_address, self.REQUEST_HANDLER)


class ThreadingServer(ThreadingMixIn, Server):
	""" A threading SCGI WSGI server. """
	MULTITHREAD = True

class ForkingServer(ForkingMixIn, Server):
	""" A forking SCGI WSGI server. """
	MULTIPROCESS = True


if __name__ == "__main__":
	import logging
	from socket import AF_UNIX

	def test_app(env, start_response):
		start_response("200 ok", [("content-type", "text/plain")])
		env["wsgi.errors"].write("an error")
		yield "hello"

	logging.basicConfig(level=logging.INFO)
	s = ThreadingServer(test_app)
	print "listening on", s.server_address
	s.serve_forever()
