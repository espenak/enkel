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

class EnkelError(Exception):
	""" Base class for all exceptions used in this framework.
	
	Never use this directly, but use one of the subclasses.
	"""
	def __init__(self, short_message, long_message):
		self.short_message = short_message
		self.long_message = long_message

	def __str__(self):
		return self.long_message
		

class EnkelUserError(EnkelError):
	""" Raised when an expected error occurs, like wrong user input.
	The messages must not contain any information a normal user
	should not get to see. """

class EnkelWarning(EnkelError):
	""" Raised when a unprobable and unimportant error occurrs.
	Typical use of warnings is to check if some unlikely client
	setups causes errors, and determine (from the number of warnings)
	if a fix for this client is required. """

class EnkelFatal(EnkelError):
	""" Raised when a error that should not be possible occurs. """
