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
from re import compile

class BrowserRoute(object):
	""" Route to different applications depending on browser. """
	PATTS = {
		"gecko": compile(r".*?(?<!like )(gecko|Gecko)"),
		"khtml": compile(r".*?KHTML/"),
		"msie": compile(r".*?MSIE"),
		"msie6": compile(r".*?MSIE 6.0"),
		"msie7": compile(r".*?MSIE 7.0"),
		"safari": compile(r".*?Safari"),
	}

	def __init__(self, default_app, **bt):
		"""
		@param default_app: The WSGI application used when
			none of the "bt" entries match.
		@param bt: Browser->application table. Point one of
			the keys in L{PATTS} to an WSGI application.
		"""
		self.default_app = default_app
		self.bt = bt

	def __call__(self, env, start_response):
		user_agent = env.get("HTTP_USER-AGENT")
		if user_agent:
			for key, app in self.default_app.iteritems():
				if self.PATTS[key].match(user_agent):
					return app(env, start_response)
		return self.default_app(env, start_response)
