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
from enkel.exml.info import XMLNS_FORM, XMLNS_MARKUP
from enkel.batteri.admin import XMLNS_ADMIN
from enkel.batteri.admin.validate import validate_admin


ADMIN = \
u"""
<admin xmlns="%(XMLNS_ADMIN)s">
	<applist>
		<app id="mytest" label="My test">
			<action id="create" label="Create"/>
			<action id="browse" label="Browse"/>
		</app>
	</applist>

	<selected app="mytest" action="browse"/>

	<section xmlns="%(XMLNS_MARKUP)s">
		<h>This is a test</h>
		<p>
			Really it is;)
		</p>

		<form xmlns="%(XMLNS_FORM)s"
				action="http://example.com/submit"
				submit_label="submit form"
				method="multipart">
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
	</section>
</admin>
""" % vars()


class TestValidate(TestCase):
	def test_validate_admin(self):
		validate_admin(XML(ADMIN))


def suite():
	return unit_case_suite(TestValidate)

if __name__ == '__main__':
	run_suite(suite())
