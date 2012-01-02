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

from unittest import TestCase
from cStringIO import StringIO
from sys import exc_info

from enkel.wansgli.apprunner import run_app, AppError, Response
from enkel.wansgli.testhelpers import unit_case_suite, run_suite


HEAD = "HTTP/1.1 200 OK\r\ncontent-type: text/plain\r\n"
ERRHEAD = "HTTP/1.1 500 ERROR\r\ncontent-type: text/plain\r\n"

def only_header_app(env, start_response):
	start_response("200 OK", [("Content-type", "text/plain")])
	return list() # return empty list

def simple_app(env, start_response):
	start_response("200 OK", [("Content-type", "text/plain")])
	return ["Simple app"]

def using_write_app(env, start_response):
	""" WSGI app for testing of the write function. """
	write = start_response("200 OK", [("Content-type", "text/plain")])
	write("Using write")
	return []

def mixing_write_app(env, start_response):
	""" WSGI app for tesing of mixing using the write function and iterator. """
	write = start_response("200 OK", [("Content-type", "text/plain")])
	write("Mixing write... ")
	return [" ...and iterator."]

def double_response_error_app(env, start_response):
	""" WSGI app for testing the situation when an error occurs BEFORE
	HTTP headers are sent to the browser and a traceback IS NOT supplied.

	This should produce an error, and the same will happen if start_response
	is called after HTTP headers are sent. """
	start_response("200 OK", [("Content-type", "text/plain")])
	start_response("500 ERROR", [("Content-type", "text/plain")])
	return list() # return empty list

def double_response_ok_app(env, start_response):
	""" WSGI app for testing the situation when an error occurs BEFORE
	HTTP headers are sent to the browser and a traceback is supplied.
	Should work.
	"""
	start_response("200 OK", [("Content-type", "text/plain")])
	try:
		int("jeje")
	except ValueError:
		start_response("500 ERROR", [("Content-type", "text/plain")],
				exc_info())
	return list() # return empty list


class DoubleResponseErrInResponse(object):
	""" WSGI app for testing the situation when an error occurs AFTER
	HTTP headers are sent to the browser and a traceback is supplied.

	Should re-raise the ValueError raised when "four" is sent to the
	int function.
	"""
	def __init__(self, env, start_response):
		start_response("200 OK", [("Content-type", "text/plain")])
		self.it = [1, "2", 3, "four", 5, "6"].__iter__()
		self.start_response = start_response

	def __iter__(self):
		for d in self.it:
			try:
				yield str(int(d))		# will fail on "four"
			except ValueError:
				self.start_response("500 ERROR",
						[("Content-type", "text/plain")],
						exc_info())


def noiter_app(env, start_response):
	""" An app that does not return an iterator. This is an error,
	and should raise AppError. """
	start_response("200 OK", [("Content-type", "text/plain")])
	return 10


def override_defaultheader(env, start_response):
	""" An app that overrides the default HTTP header "server".
	This should result in only one "server" header with the new value.
	"""
	start_response("200 OK", [
			("Content-type", "text/plain"),
			("Server", "xxx")
		])
	return []



class TestApprunner(TestCase):
	""" Tests the entire apprunner module. """
	def setUp(self):
		self.buf = StringIO()
		self.env = dict(SERVER_PROTOCOL="HTTP/1.1")
		self.sr = Response(self.buf, self.env)

	def test_only_header(self):
		run_app(only_header_app, self.sr)
		b = self.buf.getvalue()
		self.assert_(b.startswith(HEAD))

	def test_simple(self):
		run_app(simple_app, self.sr)
		b = self.buf.getvalue()
		self.assert_(b.startswith(HEAD))
		self.assert_(b.endswith("Simple app"))

	def test_using_write(self):
		run_app(using_write_app, self.sr)
		b = self.buf.getvalue()
		self.assert_(b.startswith(HEAD))
		self.assert_(b.endswith("Using write"))


	def test_mixing_write(self):
		run_app(mixing_write_app, self.sr)
		b = self.buf.getvalue()
		self.assert_(b.startswith(HEAD))
		self.assert_(b.endswith("Mixing write...  ...and iterator."))

	def test_double_response_error(self):
		self.assertRaises(AppError, run_app,
				double_response_error_app, self.sr)

	def test_double_response_ok(self):
		run_app(double_response_ok_app, self.sr)
		b = self.buf.getvalue()
		self.assert_(b.startswith(ERRHEAD))

	def testDoubleResponseErrInResponse(self):
		self.assertRaises(ValueError, run_app,
				DoubleResponseErrInResponse, self.sr)

	def test_noiter(self):
		self.assertRaises(AppError, run_app,
				noiter_app, self.sr)


def suite():
	return unit_case_suite(TestApprunner)

if __name__ == '__main__':
	run_suite(suite())
