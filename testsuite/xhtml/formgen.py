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
from os.path import join, dirname
from lxml.etree import RelaxNG, parse, XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.model import ds, data, dsources
from enkel.model.field.base import String, Int, Bool
from enkel.model.util import ModelData
from enkel.xhtml.formgen import Form
from enkel.xhtml import formgen
from enkel.rngdata import RNGDIR


RNG = join(RNGDIR, "xhtml-formgen.rng")


class TestXhtmlForm(TestCase):
	def _test_fieldgen(self, model, value):
		m = data.Manip(model)
		m.x = value

		form = Form("http://example.com/myform", "Submit")
		form["x"] = ModelData(m)
		form["x"].meta["x"] = {"label": "The label"}
		s = form.create()
		self.assertEquals(s.count("The label"), 1)
		RelaxNG(parse(RNG)).assertValid(XML(s))
		return s

	def test_many(self):
		model = dict(x=ds.Many(dsources.List(["a", "b", "c"])))
		s = self._test_fieldgen(model, ["a", "c"])

	def test_one(self):
		model = dict(x=ds.One(dsources.List(["a", "b", "c"])))
		s = self._test_fieldgen(model, "b")

	def test_string(self):
		model = dict(x=String(10))
		s = self._test_fieldgen(model, "hello")

	def test_bool(self):
		model = dict(x=Bool())
		s = self._test_fieldgen(model, True)

	def test_other(self):
		model = dict(x=Int())
		s = self._test_fieldgen(model, "hello")

	def test_hidden_and_readonly(self):
		m = data.Manip(dict(x=String()))
		m.x = "test"

		form = Form("http://example.com/myform", "Submit")
		form["x"] = ModelData(m)
		form["x"].display["x"] = {"hidden": True}
		s = form.create()
		RelaxNG(parse(RNG)).assertValid(XML(s))

		form["x"].display["x"] = {"readonly": True}
		s = form.create()
		RelaxNG(parse(RNG)).assertValid(XML(s))


def suite():
	return unit_case_suite(TestXhtmlForm)

if __name__ == '__main__':
	run_suite(suite())
