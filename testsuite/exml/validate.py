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
from lxml.etree import XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.exml.validate import \
		validate_section, validate_inline, validate_markup,\
		validate_formsection, validate_form
from enkel.exml.info import XMLNS_MARKUP, XMLNS_FORM


FORM = \
u"""
	<form xmlns="%(XMLNS_FORM)s"
			action="http://example.com/submit"
			submit_label="submit form"
			method="post">
		<string id="name" required="yes" typehint="String">
			<label>Name</label>
			<tooltip>>Your name</tooltip>
			<value>John Watson</value>
		</string>
		<string id="id" required="yes" typehint="Int">
			<label>Id</label>
			<tooltip>>A numeric id</tooltip>
			<error>Must be a number</error>
			<value>xx</value>
		</string>
	</form>
""" % vars()

FORMSECTION = \
u"""<section xmlns="%(XMLNS_MARKUP)s">
	<h>This is a test</h>
	<p>
		Really it is;)
	</p>

	%(FORM)s
</section>""" % vars()


SECTION = \
u"""<section xmlns="%s">
	<h>This is a test</h>
	<p>
		Really it is;)
	</p>
</section>""" % XMLNS_MARKUP

MARKUP = \
u"""<markup xmlns="%s">
	<p>a test</p>
</markup>""" % XMLNS_MARKUP

INLINE = u"""<inline xmlns="%s">
	A <strong>strong</strong> <em>person</em>.
</inline>""" % XMLNS_MARKUP


class TestValidate(TestCase):
	def test_validate_section(self):
		validate_section(XML(SECTION))
	def test_validate_markup(self):
		validate_markup(XML(MARKUP))
	def test_validate_inline(self):
		validate_inline(XML(INLINE))
	def test_validate_formsection(self):
		validate_formsection(XML(FORMSECTION))
	def test_validate_form(self):
		validate_form(XML(FORM))


def suite():
	return unit_case_suite(TestValidate)

if __name__ == '__main__':
	run_suite(suite())
