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
from enkel.model.field.base import Int
from enkel.model.formgen import AutoSort
from enkel.model.data import Manip


class First(Int):
	WEIGHT = 0
class Second(Int):
	WEIGHT = 1
class Third(Int):
	WEIGHT = 2
class Fourth(Int):
	WEIGHT = 3
class Fifth(Int):
	WEIGHT = 4


class TestFormgen(TestCase):
	def testAutoSort(self):
		model = dict(
			a = First(),
			b = Second(),
			c = Third()
		)
		s = [x for x in AutoSort(m=model)]
		self.assertEquals(s, [("m","a"), ("m","b"), ("m","c")])

		s = [x for x in AutoSort(("m","a"), ("m","c"), m=model)]
		self.assertEquals(s, [("m","a"), ("m","c")])



def suite():
	return unit_case_suite(TestFormgen)

if __name__ == '__main__':
	run_suite(suite())
