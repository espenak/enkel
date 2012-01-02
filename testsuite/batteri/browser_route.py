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
from enkel.batteri.browser_route import BrowserRoute


user_agents = (
	# gecko
	"Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4",
	"Mozilla/5.0 (X11; U; Linux i686 (x86_64); en-US; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",

	# khtml
	"Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko)",

	# msie
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",

	# safari
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; nb) AppleWebKit/522.15.5 (KHTML, like Gecko) Version/3.0.3 Safari/522.15.5",

	# opera
	"Opera/9.23 (X11; Linux x86_64; U; en)"
)


class TestBrowserRoute(TestCase):
	def check_patt(self, name):
		patt = BrowserRoute.PATTS[name]
		r = []
		for i, ua in enumerate(user_agents):
			if patt.match(ua):
				r.append(i)
		return r

	def test_gecko(self):
		r = self.check_patt("gecko")
		self.assertEquals(r, [0, 1])

	def test_kthml(self):
		r = self.check_patt("khtml")
		self.assertEquals(r, [2])

	def test_msie(self):
		r = self.check_patt("msie")
		self.assertEquals(r, [3, 4])
	def test_msie6(self):
		r = self.check_patt("msie6")
		self.assertEquals(r, [3])
	def test_msie7(self):
		r = self.check_patt("msie7")
		self.assertEquals(r, [4])

	def test_safari(self):
		r = self.check_patt("safari")
		self.assertEquals(r, [5])




def suite():
	return unit_case_suite(TestBrowserRoute)

if __name__ == '__main__':
	run_suite(suite())
