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

""" WSGI application execution.

This module is gateway independent. It can be used to run
WSGI apps given the correct information (from a gateway).
"""

from cStringIO import StringIO


class AppError(Exception):
	""" raised when errors are detected in WSGI apps. """


class Response(object):
	""" Implements PEP 333 (WSGI) start_response interface.

	When the interface says "must", i interpet it as something that
	does not require inspection/error checking. This makes for
	less overhead in error checking. But i also recognise that
	application developers can have great use of this error checking.

	TODO
	====
		Subclass Response (DebugResponse?) and extend validate_header
		to provide error checking. Should check for invalid
		characters and invalid HTTP headers.

	@ivar extra_headers: Extra HTTP headers. This dict is manipulated
			in validate_header, and all headers in the dict is added
			to the bottom of the http header.

	@cvar SEP: HTTP protocol (rfc2616 specifies this separator
			between headers. The value is "\\r\\n".

	@see: L{run_app} for an example.
	"""

	SEP = "\r\n"

	def __init__(self, ostream, env, debug=False):
		"""
		@param ostream: A object with a write() and flush() method. All
				output is sent to write().
		@param env: A WSGI environ dictionary. The only really required
				header is SERVER_PROTOCOL, but you should of course
				supply an environ according PEP 333.
		@param debug: Raise all exceptions as long as exc_info is given
				to __call__, even if start_response has not been called.
		"""
		self.status = None
		self.headers = None
		self.ostream = ostream
		self.headers_sent = False
		self.called = False
		self.env = env
		self.extra_headers = dict()
		self.debug = debug


	def __call__(self, status, headers, exc_info=None):
		self.status = status
		self.headers = headers

		if exc_info:
			if self.headers_sent or self.debug:
				raise exc_info[0],exc_info[1],exc_info[2]
		elif self.called:
			raise AppError(
"""The application may call start_response more than once, if and only if
the exc_info argument is provided. More precisely, it is a fatal error
to call start_response without the exc_info argument if start_response
has already been called within the current invocation of the application."""
			)
		self.called = True
		return self.write

	def __nonzero__(self):
		""" Nonzero if __call__ has been run. """
		return self.called


	def validate_header(self, name, value):
		""" Before L{generate_headers} adds a header to its buffer,
		this method is called. Subclasses can add error checking
		and add headers to the self.extra_headers dict. Extra headers
		are added last in the HTTP header.

		Does nothing by defalt.

		@param name: HTTP header name. Always in lowercase.
	 	@param value: HTTP header value.
		"""


	def generate_headers(self):
		""" Genreate http headers.
		If the app does not supply "server" or "date" headers,
		they are added. "server" header defaults to the C{server_info}
		parameter to L{__init__}
		"""
		buf = StringIO()

		# Status-Line (HTTP-Version SP Status-Code SP Reason-Phrase CRLF)
		buf.write("%s %s%s" % (self.env["SERVER_PROTOCOL"],
				self.status, self.SEP))

		# Add app-supplied headers
		for name, value in self.headers:
			name = name.lower()
			self.validate_header(name, value)
			buf.write("%s: %s%s" % (name, value, self.SEP))

		# Add extra headers
		for name, value in self.extra_headers.iteritems():
			buf.write("%s: %s%s" % (name, value, self.SEP))

		return buf.getvalue()


	def send_headers(self):
		self.ostream.write(self.generate_headers())
		self.ostream.write(self.SEP)
		self.headers_sent = True

	def write(self, block):
		""" Send data-block to client.
		Send headers on first invocation.

		Handling of the "content-length" header
		=======================================
			The content-length header is ignored.. If supplied, it is
			sent to the client, but no attempt is made to stop writing
			when "content-length" bytes have been written.
		"""
		if not self.headers_sent:
			self.send_headers()
		self.ostream.write(block)
		# WSGI specifies that flushing of the output buffer is required
		# to guarantee that data is really recieved.
		self.ostream.flush()



def run_app(app, responseobj):
	""" Run a WSGI app.

	Example (run a app without using a server)
	==========================================
		>>> def simple_app(environ, start_response):
		... 	start_response("200 OK", [("Content-type", "text/plain")])
		... 	return ["A simple app"]

		>>> from cStringIO import StringIO
		>>> buf = StringIO()
		>>> env = dict(SERVER_PROTOCOL="HTTP/1.1")
		>>> run_app(simple_app, Response(buf, env))
		>>> buf.getvalue()
		'HTTP/1.1 200 OK\\r\\ncontent-type: text/plain\\r\\n\\r\\nA simple app'

	@param app: A WSGI app.
	@param responseobj: A L{Response} object.
	"""
	result = app(responseobj.env, responseobj)
	first_block = None

	if not hasattr(result, "__iter__"):
		raise AppError("the application must return an iterable.")

	try:
		for block in result:
			# we ignore empty blocks
			if block:
				# make sure start_response() has been invoked
				if responseobj:
					responseobj.write(block)
				else:
					raise AppError(
"""the application must invoke the start_response() callable before
the iterable yields its first body string, so that the server can send
the headers before any body content."""
					)

		# send headers even if body is empty
		if not responseobj.headers_sent:
			responseobj.send_headers()

	finally:
		# "result" might have a close method, in which
		# case WSGI specifies that it must be invoked.
		if hasattr(result, "close"):
			result.close()



def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
