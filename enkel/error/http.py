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

from core import EnkelUserError


N_ = lambda string: string


class HttpUserError(EnkelUserError):
	""" Base class for HTTP user errors. Never used directly.
	
	@cvar NUMBER: The http error number. Subclasses defines this.
	"""
	NUMBER = None
	def __init__(self, short_message, long_message):
		"""
		@note: "short_message" is a unicode object and can therefore not
		be sent used as a wsgi start_response status message. To get
		the status message, use
		BaseHTTPServer.BaseHTTPRequestHandler.responses (in the
		python standard library) and L{NUMBER} to create a status
		message.

		@param short_message: A short message hinting at the problem.
		@param long_message: A longer description of the problem.
		"""
		EnkelUserError.__init__(self,
				"%d %s" % (self.NUMBER, short_message), long_message)

	def __str__(self):
		return "%(short_message)s: %(long_message)s" % self.__dict__


class Http404(HttpUserError):
	""" The server has not found anything matching the Request-URI. """
	NUMBER = 404
	def __init__(self, short_message = N_("Page not found"),
			long_message = N_("Could not find anything on the server mathing the requested URI")):
		HttpUserError.__init__(self, short_message, long_message)

class Http403(HttpUserError):
	""" The server understood the request, but is refusing to fulfill it.
	Authorization will not help and the request SHOULD NOT be repeated. """
	NUMBER = 403
	def __init__(self, long_message, short_message=N_("Forbidden")):
		"""
		@param long_message: Should describe why the URI is forbidden.
				Make sure not to say things like "password is wrong" if
				username is correct but password is wrong. This makes
				brute force authentication guessing easier. Say
				"authentication failed" or something similar. Of
				course Http403 can be raised for other issues than
				authentication failure.
		"""
		HttpUserError.__init__(self, short_message, long_message)
