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

""" Cookie helpers.

WARNING
=======
	Unlike the standard Cookie module, this interface does
	not encode the cookie value, so if you wish to store special
	characters, you have to encode the value.
"""

from datetime import datetime

from enkel.wansgli.utils import rfc1123_date
from enkel.wansgli.env import parse_value


def get_cookies(env):
	""" Lookup cookies in the WSGI environ dict.

	Example
	=======
		>>> env = dict(HTTP_COOKIE="sid=ax33d; name=John Peters")
		>>> get_cookies(env)
		{'name': 'John Peters', 'sid': 'ax33d'}

	@param env: WSGI environ dict.
	@return: dict with cookie-name as key and cookie-value as value.
			Returns None when no cookie is found.
	"""
	c = env.get("HTTP_COOKIE")
	if c:
		return parse_value(c)
	else:
		return None


class Cookie(object):
	""" A http cookie interface.
	
	Unlike the standard Cookie module, this class only works
	with a single cookie, and provides a simple interface
	for defining cookies.

	Usage
	=====
		>>> from datetime import timedelta, datetime
		>>> c = Cookie("name", "John Peters")
		>>> print c
		set-cookie: name=John Peters


		Persistant cookies
		------------------
		You can specify a timeout or a expiration date.

		>>> c.expires = datetime(2010, 12, 24)
		>>> print c
		set-cookie: name=John Peters; expires=Fri, 24 Dec 2010 00:00:00 GMT

		Timeouts are specified like this:

		>>> c.set_timeout(timedelta(days=10))


		Getting headers for WSGI
		------------------------
		>>> c = Cookie("id", "axTTT")
		>>> c.get_httpheader()
		('set-cookie', 'id=axTTT')


	@ivar name: The name of the cookie.
	@ivar value: The value of the cookie.
	@ivar domain: The cookie domain. Browsers will only send the cookie
			when revisiting this domain. Defaults to None, which most
			browsers translates to "use current domain".
	@ivar path: Cookie path. Browsers will only send the cookie when
			when revisiting this path. Defaults to None, which most
			browsers translates to "use current path".
	@ivar expires: The expiration date of the cookie as a datetime.datetime
			object. Defaults to None (no timeout). Note that if you want
			to set this to the current time you should use datetime.utcnow(),
			since cookies work in GMT/UTC time.

	@cvar HTTP_HEADER: The http header name used to set cookies.
	@cvar VERSION: The cookie version used.
	"""
	HTTP_HEADER = "set-cookie"
	VERSION = "1"
	def __init__(self, name, value, timeout=None):
		"""
		@param name: The name of the cookie.
		@param value: The value of the cookie.
		@param timeout: sent to L{set_timeout} if not None.
		"""
		self.name = name
		self.value = value
		self.domain = None
		self.expires = None
		self.path = None
		if timeout:
			self.set_timeout(timeout)

	def set_timeout(self, timeout):
		""" Set the expiration relative to the current time.
		@param timeout: A datetime.timedelta object.
		"""
		self.expires = datetime.utcnow() + timeout

	def get_httpheader(self):
		""" Get the http header like WSGI likes it.
		@return: (header-name, header-value) pair.
		"""
		v = ["%s=%s" % (self.name, self.value)]
		if self.expires:
			v.append("expires=%s" % rfc1123_date(self.expires))
		if self.path:
			v.append("path=%s" % self.path)
		if self.domain:
			v.append("domain=%s" % self.domain)
		return self.HTTP_HEADER, "; ".join(v)

	def __str__(self):
		return "%s: %s" % self.get_httpheader()


def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
