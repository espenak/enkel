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

from time import sleep
from random import randint


def simple_app(environ, start_response):
	""" A VERY simple WSGI application. """
	start_response("200 OK", [("Content-type", "text/plain")])
	return ["This is a simple test app!"]


def sleep_app(environ, start_response):
	""" A app that sleeps for 2 seconds befor it returns. """
	start_response("200 OK", [("Content-type", "text/plain")])
	sec = 2
	sleep(sec)
	return ["Slept for %d sec" % sec]
