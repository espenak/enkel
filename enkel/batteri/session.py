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

from enkel.cookie import Cookie, get_cookies
from enkel.session.backend import NoSuchSessionError


class StartResponseWrapper(object):
	""" Used by SessionMiddleware. """
	def __init__(self, start_response, cookie):
		self.start_response = start_response
		self.cookie = cookie

	def __call__(self, status, headers, exc_info=None):
		headers.append(self.cookie.get_httpheader())
		return self.start_response(status, headers, exc_info)


class SessionMiddleware(object):
	""" A session middleware.

	Test/Example
	============
		>>> from enkel.wansgli.apptester import AppTester
		>>> from enkel.session.memory import MemorySession

		>>> def myapp(env, start_response):
		... 	start_response("200 OK", [("Content-type", "text/plain")])
		... 	session = env["enkel.session"]
		... 	if "num" in session:
		... 		session["num"] += 1
		... 	else:
		... 		session["num"] = 0
		... 	return ["This is call number %(num)d to this app" % session]

		>>> class MyBackend(MemorySession):
		... 	def generate_sid(self):
		... 		return "xxAb"

		>>> b = MyBackend()
		>>> sessionapp = SessionMiddleware(myapp, b)

		>>> AppTester(sessionapp).run_get().body
		'This is call number 0 to this app'

		>>> t = AppTester(sessionapp)
		>>> t.set_env("HTTP_COOKIE", "sid=xxAb")
		>>> t.run_get().body
		'This is call number 1 to this app'

	@cvar ENV_KEY: The environ key used to contain the session.
	"""
	ENV_KEY = "enkel.session"
	def __init__(self, app, backend, cookiename="sid",
				cookiedomain=None, cookiepath="/"):
		"""
		@param app: A WSGI application.
		@param backend: A session backend following the
				L{enkel.session.backend.SessionBackend} interface.
		@param cookiename: The name of the session cookie.
		@param cookiedomain: See L{enkel.cookie.Cookie.domain}.
		@param cookiepath: See L{enkel.cookie.Cookie.path}.
		"""
		self.app = app
		self.backend = backend
		self.cookiename = cookiename
		self.cookiedomain = cookiedomain
		self.cookiepath = cookiepath

	def __call__(self, env, start_response):

		# import info from cookie
		cookies = get_cookies(env)
		session = None
		if cookies and self.cookiename in cookies:
			try:
				sid = cookies[self.cookiename]
			except KeyError:
				pass
			else:
				try:
					session = self.backend.load(sid)
				except NoSuchSessionError:
					pass

		if session == None:
			session = dict()
			sid = self.backend.generate_sid()
		env[self.ENV_KEY] = session

		# create new cookie
		cookie = Cookie(self.cookiename, sid)
		cookie.path = self.cookiepath
		cookie.domain = self.cookiedomain
		cookie.set_timeout(self.backend.timeout)

		# run app
		sr = StartResponseWrapper(start_response, cookie)
		for buf in self.app(env, sr):
			yield buf
		self.backend.save(sid, session)



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
