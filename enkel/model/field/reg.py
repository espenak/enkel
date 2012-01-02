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

""" Fields using regular expression matching. """

import re

from interface import FieldValidationError, N_
from base import String


class RegString(String):
	""" A interface for fields using regular expression matching.

	@cvar PATT: A regular expression used to match the value in
			L{validate}.
	@cvar ERRMSG: A error messaged used when raising
			L{interface.FieldValidationError}.
	"""
	PATT = None
	ERRMSG = None
	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If String.validate fails or
				if value do not match L{PATT}.
		"""
		if not self.required and not value:
			return
		super(RegString, self).validate(fieldname, value)
		if not self.PATT.match(value):
			raise FieldValidationError(fieldname, value, self.ERRMSG)


class IdString(RegString):
	""" A String field only allowed to contain a-z, 0-9, '-' and '_'. """
	PATT = re.compile("^[a-z0-9_-]+$")
	ERRMSG = N_("can only contain lower-case english letters (a-z), "\
		"numbers (0-9), '_' and '-'.")
	WEIGHT = 100
