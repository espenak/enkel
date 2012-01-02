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
from pkg_resources import resource_filename
from os.path import join, isfile
from os import listdir, remove
from shutil import copy, rmtree
from tempfile import mkdtemp, mkstemp
from lxml.etree import XML

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.apptester import AppTester
from enkel.batteri.admin import admin, validate
from enkel.batteri.staticcms.edit import StaticCmsEdit
from enkel.rngdata import RNGDIR



class TestEdit(TestCase):
	def setUp(self):
		self.tmpfolder = mkdtemp()
		postsfolder = resource_filename(__name__, "posts")
		for filename in listdir(postsfolder):
			copy(join(postsfolder, filename), self.tmpfolder)

		fd, self.configfile = mkstemp()
		open(self.configfile, "wb").write("""
[main]
posts_folder = %s
theme_folder = themes/default/
process_command = echo '%%(xsltfile)s %%(postlist_file)s'
sync_command = echo 'sync'""" % self.tmpfolder)

		self.admin = admin.Admin("admin.xsl", pretty=True)
		self.admin.add("s", StaticCmsEdit, "Static cms",
				self.configfile)
		self.admin.compile()


	def tearDown(self):
		rmtree(self.tmpfolder)
		remove(self.configfile)

	def test_browse(self):
		t = AppTester(self.admin, url="http://example.com/s/browse")
		r = t.run_get()
		validate.validate_admin(XML(r.body))

	def test_create(self):
		t = AppTester(self.admin, url="http://example.com/s/create")
		r = t.run_get()
		validate.validate_admin(XML(r.body))

	def test_edit(self):
		p = [("id", "utf8test")]
		t = AppTester(self.admin, p, url="http://example.com/s/edit")
		r = t.run_get()
		validate.validate_admin(XML(r.body))

	def test_save(self):
		p = [
			("e_id", "hello_world"),
			("e_heading", "Hello World"),
			("e_summary", "This is a test"),
			("e_tags", "testtag, infotag"),
			("e_post", "<p>Welcome to the test post</p>")
		]
		t = AppTester(self.admin, p, url="http://example.com/s/save")
		r = t.run_get()
		validate.validate_admin(XML(r.body))

		path = join(self.tmpfolder, "hello_world")
		self.assert_(isfile(path))

		post = open(path, "rb").read()
		self.assert_(post.count("testtag", 1))
		self.assert_(post.count("infotag", 1))

	def test_save_error(self):
		t = AppTester(self.admin, [], url="http://example.com/s/save")
		r = t.run_get()
		validate.validate_admin(XML(r.body))


	def test_delete(self):
		l1 = len(listdir(self.tmpfolder))
		p = [("id", "utf8test")]
		t = AppTester(self.admin, p, url="http://example.com/s/delete")
		r = t.run_get()
		self.assertEquals(len(listdir(self.tmpfolder)), l1-1)
		validate.validate_admin(XML(r.body))





def suite():
	return unit_case_suite(TestEdit)

if __name__ == '__main__':
	run_suite(suite())
