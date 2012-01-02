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
from datetime import date, time, datetime
from lxml.etree import XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.exml.formgen import Form
from enkel.exml.validate import validate_form
from enkel.model.data import Manip
from enkel.model.util import ModelData
from enkel.model.ds import One, Many
from enkel.model.dsources import Dict
from enkel.model.field.base import Int, Long, Float, String, Text,\
		Date, DateTime, Time, Bool


class TestFormgen(TestCase):
	def checkField(self, fieldobj, value, expected):
		model = dict(a = fieldobj)
		manip = Manip(model)
		manip.a = value
		form = Form("http://example.com/submit", "send")
		form["x"] = ModelData(manip)
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</%s>" % expected), 1)

	def testTypes(self):
		self.checkField(Bool(), True, "bool")
		self.checkField(Int(), 10, "int")
		self.checkField(Long(), 10L, "long")
		self.checkField(Float(), 10.0, "float")
		self.checkField(String(), "hello", "string")
		self.checkField(String(1000), "long hello", "longstring")
		self.checkField(Text(), "hello world", "text")
		self.checkField(Date(), date(2006, 12, 24), "date")
		self.checkField(Time(), time(6, 21), "time")
		self.checkField(DateTime(),
				datetime(2006, 12, 24, 6, 21), "datetime")

	def test_read_only_and_hidden_and_xmlns(self):
		model = dict(a = Int())
		manip = Manip(model)
		form = Form("http://example.com/submit", "send")
		form["x"] = ModelData(manip)

		# test read only
		form["x"].display["a"] = {"readonly": True}
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</readonly>"), 1)
		self.assertEquals(xml.count("xmlns="), 1)

		# test hidden
		form["x"].display["a"] = {"hidden": True}
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</hidden>"), 1)

		# test disable namespace
		form.xmlns = None
		xml = form.create()
		self.assertEquals(xml.count("xmlns="), 0)
		form.xmlns = "XXXX"
		xml = form.create()
		self.assertEquals(xml.count("xmlns=\"XXXX\""), 1)


	def test_many_and_one(self):
		lang = Dict(dict(
			nb = "Norwegian",
			en = "English",
			dk = "Danish"
		))
		form = Form("http://example.com/submit", "send")

		model = dict(a=One(lang))
		manip = Manip(model)
		manip.a = "en"
		form["x"] = ModelData(manip)
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</one>"), 1)
		self.assertEquals(xml.count("</item>"), 2)
		self.assertEquals(xml.count("</sel_item>"), 1)

		model = dict(a=Many(lang))
		manip = Manip(model)
		manip.a = ["en", "nb"]
		form["x"] = ModelData(manip)
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</many>"), 1)
		self.assertEquals(xml.count("</item>"), 1)
		self.assertEquals(xml.count("</sel_item>"), 2)

		form["x"].display["a"] = {"hidden": True}
		xml = form.create()
		validate_form(XML(xml))
		self.assertEquals(xml.count("</hidden>"), 2)

		form["x"].display["a"] = {"readonly": True}
		self.assertRaises(ValueError, form.create)



def suite():
	return unit_case_suite(TestFormgen)

if __name__ == '__main__':
	run_suite(suite())
