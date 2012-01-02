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
import datetime

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.model.field.base import *


class TestBase(TestCase):
	def testField(self):
		n = Field(required=False)
		self.assertEquals(n.to_unicode(None), u"")
		self.assertEquals(n.to_unicode(20), u"20")
		self.assertEquals(n.to_unicode(None), u"")

		A = type("A", (Field,), dict(WEIGHT=n.WEIGHT))
		self.assert_(n == A())
		A = type("A", (Field,), dict(WEIGHT=n.WEIGHT + 1))
		self.assert_(n < A())
		A = type("A", (Field,), dict(WEIGHT=n.WEIGHT - 1))
		self.assert_(n > A())

	def testBool(self):
		n = Bool()
		self.assertEquals(n.from_unicode(u"x"), True)
		self.assertEquals(n.from_unicode(u""), False)

		self.assertRaises(FieldValidationError, n.validate, "n", "10")
		self.assertRaises(FieldValidationError, n.validate, "n", 10)
		self.assert_(isinstance(n.to_unicode(True), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", None)
		n.validate("n", False)

	def testInt(self):
		n = Int()
		self.assertEquals(n.from_unicode(u"10"), 10)
		self.assertEquals(n.from_unicode(u"yess"), None)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertRaises(FieldValidationError, n.validate, "n", "10")
		self.assertRaises(FieldValidationError, n.validate, "n", 10L)
		self.assert_(isinstance(n.to_unicode(10L), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", None)
		n.validate("n", 10)
		Int(required=False).validate("n", None)

	def testLong(self):
		n = Long()
		self.assertEquals(n.from_unicode(u"20"), 20L)
		self.assertEquals(n.from_unicode(u"yess"), None)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertRaises(FieldValidationError, n.validate, "n", "10")
		self.assertRaises(FieldValidationError, n.validate, "n", None)
		self.assert_(isinstance(n.to_unicode(10), unicode))
		n.validate("n", 10)
		n.validate("n", 10L)
		Long(required=False).validate("n", None)

	def testFloat(self):
		n = Float()
		self.assertEquals(n.from_unicode(u"10"), 10.0)
		self.assertEquals(n.from_unicode(u"yess"), None)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertRaises(FieldValidationError, n.validate, "n", "10.0")
		self.assertRaises(FieldValidationError, n.validate, "n", 10)
		self.assert_(isinstance(n.to_unicode(10.0), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", None)
		n.validate("n", 10.0)
		Float(required=False).validate("n", None)

	def testString(self):
		n = String(5)
		self.assertEquals(n.from_unicode(u"hello"), u"hello")
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assert_(n < String(100))
		n.validate("n", u"12345")
		self.assertRaises(FieldValidationError, n.validate, "n", "hmm")
		self.assertRaises(FieldValidationError, n.validate, "n", u"123456")
		self.assert_(isinstance(n.to_unicode("hello"), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", None)
		String(required=False).validate("n", None)

	def testDate(self):
		n = Date()
		d = datetime.date(2006, 12, 24)
		self.assertEquals(n.from_unicode(u"2006-12-24"), d)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertEquals(n.to_unicode(d), u"2006-12-24")
		self.assert_(isinstance(n.to_unicode(d), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", "wrong")
		Date(required=False).validate("n", None)

	def testTime(self):
		n = Time()
		t = datetime.time(6, 33, 57)
		self.assertEquals(n.from_unicode(u"06:33:57"), t)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertEquals(n.to_unicode(t), u"06:33:57")
		self.assert_(isinstance(n.to_unicode(t), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", "wrong")
		Time(required=False).validate("n", None)

	def testDateTime(self):
		n = DateTime()
		d = datetime.datetime(2006, 12, 24, 6, 33, 58)
		self.assertEquals(n.from_unicode(u"2006-12-24 06:33:58"), d)
		self.assertRaises(ValueError, n.from_unicode, "10")

		self.assertEquals(n.to_unicode(d), u"2006-12-24 06:33:58")
		self.assert_(isinstance(n.to_unicode(d), unicode))
		self.assertRaises(FieldValidationError, n.validate, "n", "wrong")
		DateTime(required=False).validate("n", None)



def suite():
	return unit_case_suite(TestBase)

if __name__ == '__main__':
	run_suite(suite())
