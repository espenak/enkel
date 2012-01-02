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

""" Validation and utilities for the enkel xml languages.


Markup
======
	You often find that you want both site-admins and normal users to
	submit information in a structured way. This often occur in
		- forums
		- cmss
		- wikis
	And many other systems. For these situations enkel supplies a
	markup language in the U{http://enkel.wsgi.net/xml/markup}
	namespace. See the URL for documentation.
"""


__all__ = ["formgen", "info", "validate"]
