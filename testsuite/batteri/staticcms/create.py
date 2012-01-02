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

"""
Tests both create and preprocess.
"""
from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from os.path import split, dirname, join, abspath
from os import mkdir, listdir
from lxml.etree import parse, RelaxNG
from pkg_resources import resource_filename

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.batteri.staticcms.create import prepare_env
from enkel.batteri.staticcms.preprocess import preprocess
from enkel.rngdata import RNGDIR


SRNGDIR = join(RNGDIR, "staticcms")


class Test_create(TestCase):
	def setUp(self):
		self.tmp = mkdtemp()
		self.postsfolder = resource_filename(__name__, "posts")

	def tearDown(self):
		rmtree(self.tmp)


	def test_preprocess(self):
		posts = join(self.tmp, "posts")
		tags = join(self.tmp, "tags")
		preprocess(posts, tags, self.postsfolder)

		rng = RelaxNG(parse(join(SRNGDIR, "posts.rng")))
		rng.assertValid(parse(posts))
		res = open(posts, "rb").read()
		self.assertEquals(res.count("<post "), 3)

		rng = RelaxNG(parse(join(SRNGDIR, "tags.rng")))
		rng.assertValid(parse(tags))
		res = open(tags, "rb").read()
		self.assertEquals(res.count("<tag "), 3)


	def test_prepare_env(self):
		tmp = join(self.tmp, "x")
		mkdir(tmp)

		# we use the postsfolder as themefolder because we only
		# need to check that a folder is copied.
		prepare_env(tmp, self.postsfolder, self.postsfolder)

		files = ["posts.xml", "tags.xml", "theme"]
		files.sort()

		tmpfiles = listdir(tmp)
		tmpfiles.sort()

		self.assertEquals(files, tmpfiles)


def suite():
	return unit_case_suite(Test_create)

if __name__ == '__main__':
	run_suite(suite())
