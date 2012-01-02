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

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.apptester import AppTester
from enkel.batteri.error_handler import ErrorHandler
from enkel.error import EnkelUserError
from enkel.error.http import Http404


def user_err_app(env, start_response):
	raise EnkelUserError("short", "long")
def http_err_app(env, start_response):
	raise Http404()
def other_err_app(env, start_response):
	raise Exception("something is wrong")


class TestErrorHandler(TestCase):
	def testUserError(self):
		a = ErrorHandler(user_err_app, use_log=False)
		t = AppTester(a)
		b = t.run_get().body
		self.assert_(b.count("<h1>short"))

	def testHttpError(self):
		a = ErrorHandler(http_err_app, use_log=False)
		t = AppTester(a)
		b = t.run_get().body
		self.assert_(b.count("404"))

	def testOtherError(self):
		a = ErrorHandler(other_err_app, use_log=False)
		t = AppTester(a)
		b = t.run_get().body
		self.assertEquals(b, 'Internal server error')



def suite():
	return unit_case_suite(TestErrorHandler)

if __name__ == '__main__':
	run_suite(suite())
