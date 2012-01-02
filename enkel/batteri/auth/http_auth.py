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

from base64 import b64decode

from userdb_interface import AuthorizationError, DomainError

USER_ENV = "enkel.batteri.auth"


class BasicHttpAuth(object):
	def __init__(self, app, userdb, domain, realm):
		"""
		@param app: A wsgi application to run if authentication is
				passed.
		@type userdb: L{userdb_interface.UserDb}
		@param userdb: A UserDb.
		@param domain: The domain which the application belongs to.
				Users accessing the application must also be members
				of this domain.
		@param realm: A descriptive value identifying the authentication
				realm.
		"""
		self.app = app
		self.userdb = userdb
		self.domain = domain
		self.realm = realm

	def on_unauthorized(self, env, start_response):
		start_response("401 Unauthorised", [
			("www-authenticate", 'Basic realm="%s"' % self.realm),
			("content-type", "text/plain")
		])
		return ["Unauthorized"]

	def on_forbidden(self, env, start_response):
		start_response("403 Forbidden", [("content-type", "text/plain")])
		return ["Forbidden"]

	def __call__(self, env, start_response):
		"""
		If the authentcation is successful, (user, domain)
		is placed in env[L{USER_ENV}].
		"""
		auth = env.get("HTTP_AUTHORIZATION")
		if auth and auth.startswith("Basic "):
			uname, pwd = b64decode(auth[6:]).split(":")
			try:
				self.userdb.authenticate(env, uname, pwd, self.domain)
			except AuthorizationError:
				return self.on_unauthorized(env, start_response)
			except DomainError:
				return self.on_forbidden(env, start_response)
			env[USER_ENV] = (uname, self.domain)
			return self.app(env, start_response)
		return self.on_unauthorized(env, start_response)
