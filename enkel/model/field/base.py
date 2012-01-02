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

""" Base L{interface.Field} implementations. """

import datetime
from time import strptime

from interface import FieldValidationError, Field, N_



class Bool(Field):
	""" Boolean field. """
	WEIGHT = 250
	def __init__(self):
		super(Bool, self).__init__(required=True)

	def from_unicode(self, value):
		self.check_unicode(value)
		return bool(value)

	def validate(self, fieldname, value):
		if not self.required and value == None:
			return
		if self.required and value == None or not isinstance(value, bool):
			raise FieldValidationError(fieldname, value,
					N_("must be boolean (True or False)"))



class Int(Field):
	""" Integer field (can contain both positive and negative numbers). """
	WEIGHT = 300
	def from_unicode(self, value):
		self.check_unicode(value)
		try:
			return int(value)
		except:
			return self.get_default()

	def validate(self, fieldname, value):
		if not self.required and value == None:
			return
		if self.required and value == None or not isinstance(value, int):
			raise FieldValidationError(fieldname, value,
					N_("must be a whole number"))


class Long(Field):
	""" Long integer field (can contain both positive and negative numbers). """
	WEIGHT = 400
	def from_unicode(self, value):
		self.check_unicode(value)
		try:
			return long(value)
		except:
			return self.get_default()

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If required and value is None or
				if value is not an int or long.
		"""
		if not self.required and value == None:
			return
		if self.required and value == None or not \
				(isinstance(value, int) or isinstance(value, long)):
			raise FieldValidationError(fieldname, value,
					N_("must be a whole number"))


class Float(Field):
	""" Floating point number. """
	WEIGHT = 500
	def from_unicode(self, value):
		self.check_unicode(value)
		try:
			return float(value)
		except:
			return self.get_default()
	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If required and value is None or
				if value is not a float.
		"""
		if not self.required and value == None:
			return
		if self.required and value == None or not isinstance(value, float):
			raise FieldValidationError(fieldname, value,
					N_("must be a floating-point number"))



class String(Field):
	""" Unicode strings with a maximum length.

	@ivar maxlength: The maximum number of bytes allowed in the field.
	@ivar minlength: The minimum number of bytes allowed in the field.
	@cvar LONG_STRING: If the string has more than LONG_STRING
			characters it is counted as a long string. This can be used
			to separate short and long strings.
	@cvar LONG_WEIGHT: The weight of the field if it is a L{LONG_STRING}.
	"""
	LONG_STRING = 50
	WEIGHT = 200
	LONG_WEIGHT = 1100
	def __init__(self, maxlength=20, minlength=1,
				required=True):
		"""
		@param maxlength: The maximum number of bytes allowed. If
				maxlength > LONG_STRING, WEIGHT is changed to LONG_WEIGHT.
		@param minlength: Minimum numbers of bytes allowed.
		@param required: see L{Field.__init__}.
		"""
		self.required = required
		self.maxlength = maxlength
		self.minlength = minlength
		if maxlength > self.LONG_STRING:
			self.WEIGHT = self.LONG_WEIGHT

	def from_unicode(self, value):
		self.check_unicode(value)
		return value

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If value is not unicode,
				if value contains more or less than the allowed
				number of characters, or if the field is required
				and value == None.
		"""
		if not self.required and bool(value) == False:
			return

		if isinstance(value, unicode):
			l = len(value)
			if l < self.minlength:
				err = N_("to few characters")
			elif l > self.maxlength:
				err = N_("to many characters")
			else:
				return
		else:
			err = N_("must be a unicode string")
		raise FieldValidationError(fieldname, value, err)


class Text(Field):
	""" Unicode string of unlimited/undefined size. """
	WEIGHT = 1200
	def __init__(self, required=True):
		"""
		@param required: see L{Field.__init__}.
		"""
		self.required = required

	def from_unicode(self, value):
		self.check_unicode(value)
		return value

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If value is not a str or
				if the field is required and value == None.
		"""
		if not self.required and bool(value) == False:
			return
		if not isinstance(value, unicode):
			raise FieldValidationError(fieldname, value,
					N_("must be a unicode string"))


class Date(Field):
	""" A date field using datetime.date. """
	FORMAT = "%Y-%m-%d" # iso-8601 date format (yyyy-mm-dd)
	WEIGHT = 700
	def from_unicode(self, value):
		""" Convert from unicode using time.strptime and L{FORMAT}. """
		self.check_unicode(value)
		try:
			d = strptime(value, self.FORMAT)
		except ValueError:
			return self.get_default()
		return datetime.date(*d[0:3])

	def to_unicode(self, value):
		""" Convert to unicode using value.strftime and L{FORMAT}. """
		if value == None:
			return u""
		else:
			return unicode(value.isoformat())

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If required and value is None
				or if value is not an instance of datetime.date.
		"""
		if not self.required and value == None:
			return
		if not isinstance(value, datetime.date):
			raise FieldValidationError(fieldname, value,
					N_("must be a datetime.date object"))

class Time(Field):
	""" A time field for representing the time of day using datetime.time. """
	FORMAT = "%H:%M:%S" # hh:mm:ss
	WEIGHT = 800
	def from_unicode(self, value):
		""" Convert from unicode using time.strptime and L{FORMAT}. """
		self.check_unicode(value)
		try:
			d = strptime(value, self.FORMAT)
		except ValueError:
			return self.get_default()
		return datetime.time(*d[3:6])

	def to_unicode(self, value):
		""" Convert to unicode using value.strftime and L{FORMAT}. """
		if value == None:
			return u""
		else:
			return unicode(value.strftime(self.FORMAT))

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If required and value is None
				or if value is not an instance of datetime.time.
		"""
		if not self.required and value == None:
			return
		if not isinstance(value, datetime.date):
			raise FieldValidationError(fieldname, value,
					N_("must be a datetime.time object"))


class DateTime(Field):
	""" A timestamp field using datetime.datetime. """
	FORMAT = "%Y-%m-%d %H:%M:%S" # yyyy-mm-dd hh-mm-ss
	WEIGHT = 900
	def from_unicode(self, value):
		""" Convert from uniocde using time.strptime and L{FORMAT}. """
		self.check_unicode(value)
		try:
			d = strptime(value, self.FORMAT)
		except ValueError:
			return self.get_default()
		return datetime.datetime(*d[0:6])

	def to_unicode(self, value):
		""" Convert to unicode using value.strftime and L{FORMAT}. """
		if value == None:
			return u""
		else:
			return unicode(value.strftime(self.FORMAT))

	def validate(self, fieldname, value):
		"""
		@raise FieldValidationError: If required and value is None
				or if value is not an instance of datetime.datetime.
		"""
		if not self.required and value == None:
			return
		if not isinstance(value, datetime.datetime):
			raise FieldValidationError(fieldname, value,
					N_("must be a datetime.datetime object"))
