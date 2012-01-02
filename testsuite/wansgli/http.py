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
import os, sys
from time import sleep
from urllib import urlopen
from threading import Thread

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.http import Server


def myapp(env, start_response):
	start_response("200 OK", [("content-type", "text/plain")])
	yield "hello"


class TestServer(TestCase):
	def get_result(self, app):
		server_address = ("localhost", 8500)
		s = Server(app, server_address)
		s.allow_reuse_address = True
		t = Thread(target=s.handle_request)
		t.start()

		sleep(0.8) # give the server some time to start
		f = urlopen("http://%s:%d" % server_address)
		headers = f.info()
		body = f.read()
		f.close()
		return headers, body

	def test_sanity(self):
		headers, body = self.get_result(myapp)
		self.assertEquals(body, "hello")
		self.assertEquals(headers["content-type"], "text/plain")
		self.assertEquals(headers["server"], Server.server_info)
		self.assert_("date" in headers)


def suite():
	return unit_case_suite(TestServer)

if __name__ == '__main__':
	run_suite(suite())
