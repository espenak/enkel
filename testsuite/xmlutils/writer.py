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
from enkel.xmlutils.writer import XmlWriter


class TestXmlWriter(TestCase):
	def setUp(self):
		w = XmlWriter()

		w.pi("xml", version="1.0")
		w.pi_raw("pros", "shit")
		w.start_element("html")
		w.start_element("body")
		w.text_node(u"\u00e5ge")
		w.empty_element("div", attrdict={"class":"test"})
		w.end_element(2)
		self.w = w
		self.b = w.create()

	def test_closing(self):
		self.assertEquals(self.b.count("body"), 2)
		self.assertEquals(self.b.count("html"), 2)
		self.assertEquals(self.b.count("xml"), 1)
		self.assertEquals(self.b.count("div"), 1)

	def test_unicode(self):
		self.assert_(isinstance(self.b, unicode))

	def test_pi(self):
		self.assertEquals(self.b.count("<?xml version="), 1)
		self.assertEquals(self.b.count("<?pros shit?>"), 1)

	def test_textNode(self):
		self.assert_(u"\u00e5ge" in self.w.buf)


def suite():
	return unit_case_suite(TestXmlWriter)

if __name__ == '__main__':
	run_suite(suite())
