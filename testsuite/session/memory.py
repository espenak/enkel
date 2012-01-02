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
from time import sleep
from cStringIO import StringIO
from datetime import timedelta

from enkel.wansgli.testhelpers import unit_case_suite, run_suite
from enkel.session.memory import MemorySession, NoSuchSessionError


class TestMemorySession(TestCase):
	def test_load_save(self):
		ms = MemorySession()
		sid = ms.generate_sid()
		ms.save(sid, dict(name="John", age=20))
		session = ms.load(sid)
		self.assertEquals(session["name"], "John")

	def test_remove_old(self):
		m = MemorySession(timeout=timedelta(milliseconds=1),
				delete_interval=timedelta(milliseconds=1))
		sid = "xxyA"
		m.save(sid, dict(name="John", age=20))
		sleep(0.1)
		self.assertRaises(NoSuchSessionError, m.load, sid)



def suite():
	return unit_case_suite(TestMemorySession)

if __name__ == '__main__':
	run_suite(suite())
