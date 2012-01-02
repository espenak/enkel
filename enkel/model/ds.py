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

""" A interface for definition of fields linked agains external
data sources. """


from field.interface import Field, FieldValidationError


class Datasource(object):
	""" The data-source interface. A field using an external
	datasource, like L{One} and L{Many}, takes a class implementing
	this interface as first argument.

	@type field: L{field.interface.Field}
	@ivar field: Defines the datatype for members of the datasource.
	"""
	def ds_validate(self, fieldname, value):
		""" Validate value.
		@param fieldname: The name of the field.
		@param value: The value to validate.
		@raise FieldValidationError: If the validation fails.
		"""
		raise NotImplementedError()

	def ds_iter(self):
		""" Iterate over all "nodes" in the datasource yielding
		(value, label) pairs. """
		raise NotImplementedError()

	def ds_iter_unicode(self):
		""" Iterate using L{ds_iter} and convert "value" to unicode using
		L{field}.to_unicode. """
		for value, label in self.ds_iter():
			yield self.field.to_unicode(value), label


class DatasourceField(Field):
	""" Superclass for fields using a datasource.

	@ivar datasource: A object implementing the L{Datasource} interface.
	"""
	def __init__(self, datasource, required=True):
		""" 
		@param datasource: see L{datasource}.
		@param required: bool "field is required?".
		"""
		self.datasource = datasource
		self.required = required


class One(DatasourceField):
	""" Defines a field that can contain one value that validates in
	the datasource.

	In database theory, this is called a one-to-many relation. But
	the datasources are, of course, not limited to database tables. """
	def validate(self, fieldname, value):
		if not self.required and value == None:
			return
		self.datasource.ds_validate(fieldname, value)

	def from_unicode(self, value):
		return self.datasource.field.from_unicode(value)

	def to_unicode(self, value):
		return self.datasource.field.to_unicode(value)


class ManyValueInterface(object):
	def __iter__(self):
		""" Iterate over all values. """

	def __contains__(self, value):
		""" Check if value is among values. """


class Many(DatasourceField):
	""" Defines a field that can contain one to many values that validates
	in the datasource.

	The "value" passed to L{validate}, L{from_unicode} and L{to_unicode} must
	implement L{ManyValueInterface}.
	
	In database theory, this is called a many-to-many relation. But
	the datasources are, of course, not limited to database tables. """
	def validate(self, fieldname, value):
		"""
		@see: L{field.interface.Field} for more documetation.
		@param value: Described above.
		@raise FieldValidationError: If value is not an iterable.
		"""
		if not self.required and value == None:
			return
		if not hasattr(value, "__iter__"):
			raise FieldValidationError(fieldname, value,
					"must be a iterable.")
		for v in value:
			self.datasource.ds_validate(fieldname, v)

	def from_unicode(self, value):
		return [self.datasource.field.from_unicode(v)\
				for v in value]

	def to_unicode(self, value):
		return [self.datasource.field.to_unicode(v) for v in value]
