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

""" 
@var SMALL_FIELD: Defines the limit of the L{Field.WEIGHT} of
		a field before it is counted as a "big" field. This
		variable can be used to help with field classification
		when generating indexes and similar.
"""

from enkel.error import EnkelUserError



N_ = lambda string: string
SMALL_FIELD = 1000


class FieldValidationError(EnkelUserError):
	""" Raised when validation of a field fails. """
	def __init__(self, fieldname, value, long_message):
		self.fieldname = fieldname
		self.value = value
		EnkelUserError.__init__(self, N_("validation failed"), long_message)

	def __str__(self):
		return "%s: %s" % (self.fieldname, self.long_message)

	def __repr__(self):
		return "<FieldValidationError: %s>" % self.fieldname


class Field(object):
	""" Base class for all fields.
	
	@cvar WEIGHT: Used to compare a fields. Added to simplify form
			autosorting. The higher the number, the lower down in the
			form a field will be placed.
	@ivar required: field is required?
	"""
	WEIGHT = 1000
	required = True
	def __init__(self, required=True):
		self.required = required

	def validate(self, fieldname, value):
		""" Validate the value.

		@param fieldname: The name of the field.
		@param value: The value to validate.

		@raise FieldValidationError: If validation fails.
		"""
		raise NotImplementedError()

	def get_default(self):
		""" Get the default value.

		Field implementors must make sure this method returns
		instances generated on each invokation, and not static
		values. If not, the field will not be thread-safe.

		@return: The default value for this field. Defaults to None.
		"""
		return None

	def check_unicode(self, value):
		""" Can be used by L{from_unicode} to make sure value
		is unicode. """
		if not isinstance(value, unicode):
			raise ValueError("'value' must be unicode")

	def from_unicode(self, value):
		""" Cast the value from unicode to the correct type.
		If the conversion fails, the default value should be
		returned.

		If an exception is raised here because the converion
		fails, the entire point of having a system that can be
		worked with safely and validated later collapses.

		@raise ValueError: If "value" is not unicode.
		@param value: The value to cast.
		@return: The default is to return the value unchanged, but
				subclasses must override this behaviour if the native
				type is not string.
		"""
		self.check_unicode(value)
		return value

	def to_unicode(self, value):
		""" Create a unicode representation of the value.
		
		@param value: The value to cast.
		@return: The default is to return unicode(value) or u""
				if value is None, but subclasses can override this behaviour.
		"""
		if value == None:
			return u""
		else:
			return unicode(value)

	def __cmp__(self, other):
		""" Compare this field to another.

		Fields are compared by the instance variable WEIGHT.

		>>> class A(Field):
		... 	WEIGHT = 20
		>>> class B(Field):
		... 	WEIGHT = 10
		>>> a = A()
		>>> b = B()
		>>> a > b
		True
		>>> b.WEIGHT = 20
		>>> a == b
		True
		"""
		if isinstance(other, Field):
			return cmp(self.WEIGHT, other.WEIGHT)
		else:
			return 1





def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
