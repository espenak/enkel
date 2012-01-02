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
from urllib import quote_plus

from enkel.wansgli.formparse import parse_multipart, parse_query_string
from enkel.wansgli.testhelpers import unit_case_suite, run_suite



body = u"--ja\r\ncontent-disposition: form-data; name='john'" \
		u"\r\n\r\nis my \u00e5 name\r\n" \
		u"--ja\r\ncontent-disposition: form-data; name='about'; " \
		u"filename='john.txt'\r\ncontent-type: text/plain" \
		u"\r\n\r\nhello\r\n--ja--"
body = body.encode("utf-8")

class Test_parse_multipart(TestCase):
	def check_result(self, b):
		files, var = parse_multipart(
			"multipart/form-data; boundary=ja",
			len(b), StringIO(b), "utf-8")

		self.assert_("john" in var)
		self.assertEquals(var("john"), u"is my \u00e5 name")

		self.assert_("about" in files)
		self.assertEquals(files("about").read(), "hello")
		self.assertEquals(files("about").content_type, "text/plain")

	def test_standard(self):
		self.check_result(body)

	def test_nonstandard_newline(self):
		self.check_result(body.replace("\r\n", "\n"))

	def test_headers_ignorecase(self):
		self.check_result(body.replace(
				"content", "cOntenT").replace("disposition", "DISPOSITION"))

class Test_parse_query_string(TestCase):
	def test_parse_query_string(self):
		p = parse_query_string("a=jeje&b=haha&a=10", "utf-8")
		self.assertEquals(p["a"], [u"jeje", u"10"])
		self.assertEquals(p["b"], [u"haha"])
		self.assertEquals(p["b"], [u"haha"])

		name = u"\u00e5ge"
		q = "name=%s" % quote_plus(name.encode("utf-8"))
		p = parse_query_string(q, "utf-8")
		self.assertEquals(p.getfirst("name"), name)


def suite():
	return unit_case_suite(Test_parse_multipart, Test_parse_query_string)

if __name__ == '__main__':
	run_suite(suite())
