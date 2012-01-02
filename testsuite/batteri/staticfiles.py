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

from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from os import mkdir, symlink
from unittest import TestCase

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.wansgli.apptester import AppTester
from enkel.batteri.staticfiles import StaticFiles



class TestStaticFiles(TestCase):
	def setUp(self):
		self.folder = mkdtemp()

		tst = join(self.folder, "tst")
		test1 = join(self.folder, "test.txt")
		test2 = join(self.folder, "test2.txt")

		open(test1, "w").write("hello world")
		open(test2, "w").write("a test...")
		symlink(test1, join(self.folder, "test1link"))

		mkdir(tst)
		symlink(test2, join(tst, "test2link"))
	
	def test_wo_prefix(self):
		s = StaticFiles(self.folder)
		r = AppTester(s, url="http://example.com/test.txt").run_get()
		self.assertEquals(r.body, "hello world")

	def test_w_prefix(self):
		s = StaticFiles(self.folder, prefix="/my/prefix/")
		r = AppTester(s, 
				url="http://example.com/my/prefix/test2.txt").run_get()
		self.assertEquals(r.body, "a test...")

	def test_folder(self):
		s = StaticFiles(self.folder)
		r = AppTester(s, url="http://example.com").run_get()
		self.assert_(r.body_ncontains("<a href='test2.txt'>"))
		self.assert_(r.body_ncontains("test1link", 0))

	def test_folder_symlink(self):
		s = StaticFiles(self.folder, follow_symlinks=True)
		r = AppTester(s, url="http://example.com").run_get()
		self.assert_(r.body_ncontains("test1link", 2))

	def test_file_and_folder_symlink(self):
		s = StaticFiles(self.folder, follow_symlinks=True)
		r = AppTester(s, 
				url="http://example.com/tst/test2link").run_get()
		self.assertEquals(r.body, "a test...")

	def test_pattern(self):
		s = StaticFiles(self.folder, follow_symlinks=True,
				pattern="(^[a-z.]+$)|(^tst/.*$)")
		r = AppTester(s, url="http://example.com/test.txt").run_get()
		self.assertEquals(r.body, "hello world")
		r = AppTester(s, url="http://example.com/tst/").run_get()
		self.assert_(r.body_ncontains("test2link", 2))

		s = StaticFiles(self.folder, pattern="(?!^(tst)|(tst/.*)$)")
		r = AppTester(s, url="http://example.com/tst").run_get()
		self.assertEquals(r.body, "tst does not exist")

	def tearDown(self):
		rmtree(self.folder)


def suite():
	return unit_case_suite(TestStaticFiles)

if __name__ == '__main__':
	run_suite(suite())
