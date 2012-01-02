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
from xml.dom.minidom import parseString
from lxml.etree import XML, LxmlError, RelaxNG

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.model.field.xmlf import XmlField, FieldValidationError,\
		LxmlFieldValidationError


def validate1(fieldname, xml, offset):
	raise FieldValidationError(fieldname, xml, "failed")

def validate2(fieldname, xml, offset):
	try:
		XML(xml)
	except LxmlError, e:
		raise LxmlFieldValidationError(fieldname, xml, offset, e)

def validate3(fieldname, xml, offset):
	rng = RelaxNG(XML("""
		<element name='b' xmlns='http://relaxng.org/ns/structure/1.0'>
			<text/>
		</element>"""))
	try:
		rng.assertValid(XML(xml))
	except LxmlError, e:
		raise LxmlFieldValidationError(fieldname, xml, offset, e)


class TestXml(TestCase):
	def test_XmlField(self):
		f = XmlField(validate=validate1)
		self.assertRaises(FieldValidationError, f.validate,
				"x", u"hmm")
		f = XmlField(required=False)
		f.validate("x", None)

	def test_XmlField_relaxng(self):
		# lxml syntax error
		f = XmlField(validate=validate2)
		self.assertRaises(LxmlFieldValidationError, f.validate,
				"x", u"<x")

		# lxml relax-ng error
		f = XmlField(validate=validate3)
		self.assertRaises(LxmlFieldValidationError, f.validate,
				"x", u"<a/>")



def suite():
	return unit_case_suite(TestXml)

if __name__ == '__main__':
	run_suite(suite())
