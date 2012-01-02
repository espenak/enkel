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
from lxml.etree import XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.batteri.staticcms.validate_post import \
		validate_post, validate_post_field
from enkel.model.field.xmlf import XmlField


post = u"""
<post xmlns="http://enkel.wsgi.net/xml/staticcms">
        <summary>
                About us
        </summary>
        <tag>Article</tag>
        <tag>Test</tag>
        <section xmlns="http://enkel.wsgi.net/xml/markup">
			<h>About</h>
			<p>About ......</p>
        </section>
</post>"""


class Test_validate_post(TestCase):
	def test_validate_post(self):
		validate_post(XML(post))
	def test_validate_post_field(self):
		f = XmlField(validate=validate_post_field)
		f.validate("f", post)



def suite():
	return unit_case_suite(Test_validate_post)

if __name__ == '__main__':
	run_suite(suite())
