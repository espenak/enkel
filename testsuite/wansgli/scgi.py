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

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.scgi import ScgiRequestHandler


class Test_scgi(TestCase):
	def test_parse_scgi_headers(self):
		h = "SCGI\0yes\0SCRIPT_NAME\0/path\0PATH_INFO\0/to.txt\0"
		stream = StringIO("%s:%s,data" % (len(h), h))
		env = ScgiRequestHandler.parse_scgi_headers(stream)
		self.assertEquals(env,
			dict(SCRIPT_NAME="/path", PATH_INFO="/to.txt"))
		self.assertEquals(stream.read(), "data")


def suite():
	return unit_case_suite(Test_scgi)

if __name__ == '__main__':
	run_suite(suite())

