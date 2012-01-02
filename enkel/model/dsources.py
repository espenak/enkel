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

""" Simple L{ds.Datasource} implementations. """


from field.interface import FieldValidationError
from field.base import Text
from ds import Datasource


N_ = lambda string: string


class List(Datasource):
	""" A L{ds.Datasource} implementation capable of using
	"list-like" objects.
	"""
	def __init__(self, data, field=Text()):
		""" Parameters are the same as the internal variables
		described above.
		
		@param data: A container. Must at least have a __contains__(value)
				method that checks if it contains the given value and a
				__iter__() method for iteration over all values.
		@param field: Defines the datatype for members of the list.
			Defaults to L{field.base.Text}().
		"""
		self.data = data
		self.field = field

	def ds_validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If value is not in "data" or
				if the value fails to be validatated by "field".
		"""
		self.field.validate(fieldname, value)
		if not value in self.data:
			raise FieldValidationError(fieldname, value,
					N_("illegal value"))

	def ds_iter(self):
		for value in self.data:
			yield value, value


class Dict(List):
	""" A L{ds.Datasource} implementation capable of using
	"list-like" objects.

	This is the same as L{List} except "data" is a dict-like
	object. The keys in the dict are the values that are validated
	agains. The values in the dict are the "label" returned by
	L{ds_iter}.
	"""
	def ds_iter(self):
		return self.data.iteritems()
