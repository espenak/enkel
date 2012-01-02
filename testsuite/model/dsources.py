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
from enkel.model.dsources import List, Dict
from enkel.model.field.base import Int, String, FieldValidationError


class TestDsources(TestCase):
	def testList(self):
		l = [1,2,3,4,5]
		ds = List(l, Int())
		ds.ds_validate("test", 1)
		self.assertRaises(FieldValidationError,
			ds.ds_validate, "test", "1") # not int
		self.assertRaises(FieldValidationError,
			ds.ds_validate, "test", 10) # not in datasource
		l2 = [x for x, y in ds.ds_iter()]
		self.assertEquals(l, l2)
		l3 = [x for x, y in ds.ds_iter_unicode()]
		self.assertEquals(l3[0], "1")


	def testDict(self):
		d = {
			u'john': "John Peters",
			u'peter': "Peter Johnson"
		}
		ds = Dict(d, String(6))
		ds.ds_validate("test", u"john")
		self.assertRaises(FieldValidationError,
			ds.ds_validate, "test", "john") # not unicode
		self.assertRaises(FieldValidationError,
			ds.ds_validate, "test", u"Amy") # not in datasource

		l = set([y for x, y in ds.ds_iter()])
		self.assertEquals(l, set(["John Peters", "Peter Johnson"]))



def suite():
	return unit_case_suite(TestDsources)

if __name__ == '__main__':
	run_suite(suite())
