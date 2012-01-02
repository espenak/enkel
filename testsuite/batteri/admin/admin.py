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
from lxml.etree import XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.apptester import AppTester
from enkel.batteri.admin.admin import Admin, AdminApp
from enkel.batteri.admin.validate import validate_admin



class AdminTestApp(AdminApp):
	ACTIONS = dict(create=u"Create", delete=u"Delete")
	INDEX = ["create"]

	def create(self):
		self.w.start_element("p")
		self.w.text_node("'create' action selected.")
		self.w.end_element()


class TestAdmin(TestCase):
	def testIt(self):
		a = Admin("test.xsl")
		a.add(u"test", AdminTestApp, u"Test app")
		a.add(u"test2", AdminTestApp, u"Test app 2")
		a.compile()
		t = AppTester(a, [], "http://example.com/test/create")
		r = t.run_get(True)
		validate_admin(XML(r.body))


def suite():
	return unit_case_suite(TestAdmin)

if __name__ == '__main__':
	run_suite(suite())
