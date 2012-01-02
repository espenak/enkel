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

""" Data manipulation. """

from field.interface import FieldValidationError


class Manip(object):
	""" Model data manipulator.

	Models are just dict's of L{field.interface.Field} objects. Use
	Manip's to manipulate a model.

	Example
	=======
		>>> from field import base
		>>> personmodel = dict(
		... 	name = base.String(10),
		... 	email = base.String(50),
		... 	age = base.Int()
		... )
		>>> john = Manip(personmodel)
		>>> john.name = u"john"
		>>> john.age = 20


		Validation
		----------

		Fields are required as long as nothing else is spesified.

		>>> john.validate()
		Traceback (most recent call last):
		...
		FieldValidationError: email: must be a unicode string
		>>> john.email = u"john@example.com"
		>>> john.validate()


		base.Int fields must contain integers.

		>>> john.age = "wrong"
		>>> john.validate()
		Traceback (most recent call last):
		...
		FieldValidationError: age: must be a whole number


		We can also get all errors as a list

		>>> john.email = 10
		>>> john.age = "wrong"
		>>> john.info_validate()
		[<FieldValidationError: age>, <FieldValidationError: email>]



	Using string representation
	===========================
		>>> john.set_unicode(u"age", u"200")
		>>> john.age
		200

		>>> john.get_unicode("age")
		u'200'
		>>> john.age = None
		>>> john.get_unicode("age")
		u''


	Advanced example
	================
		>>> import ds, dsources

		>>> personlist = dsources.List(
		... 		["john", "jack", "amy", "bender"])
		>>> register = dict(
		... 	id = base.Int(),
		... 	title = base.String(10),
		... 	admin = ds.One(personlist),
		... 	members = ds.Many(personlist),
		... )

		>>> e = Manip(register)
		>>> e.id = 10
		>>> e.title = u"Employees"
		>>> e.admin = u"jack"
		>>> e.members = u"jack", u"amy"
		>>> e.validate()

		"admin" and "members" must be subselections of the values
		in personlist. It is actually the datasource, in this case
		a ContainerDatasource, who validates the given values. It could
		be a dictionary, database table, text-file.. and so on. And
		it is easy to create your own data-source.

		Below we see the result of invalid values to a ds.Many field.

		>>> e.members = u"john", u"jane"
		>>> e.validate()
		Traceback (most recent call last):
		...
		FieldValidationError: members: illegal value


	Importing data to a manipulator
	===============================
		
		>>> mydata = dict(xx_title=u"some people", xx_id=10,
		... 	xx_members=[u"jane", u"amy"])
		>>> e.merge(mydata, "xx_")
		>>> e.title
		u'some people'

		We can also merge from a dict with only unicode values.
		This situation ofter occurs when importing from file
		or http form input.

		>>> sdata = dict(a_title=u"hello", a_id=u"25",
		... 	a_members=[u"jane", u"bender"], a_admin=u"amy")
		>>> e.unicode_merge(sdata, "a_")
		>>> e.title
		u'hello'
		>>> isinstance(e.id, int)
		True
		>>> e.admin
		u'amy'
		>>> e.members
		[u'jane', u'bender']

	@ivar model: The model given as parameter to L{__init__}.
	"""
	def __init__(self, model, **kw):
		object.__setattr__(self, "_values", dict())
		object.__setattr__(self, "model", model)
		for key, value in kw.iteritems():
			self.__setattr__(key, value)

	def _merge(self, func, dct, prefix):
		l = len(prefix)
		for key in self.model:
			k = prefix + key
			value = dct.get(k, None)
			if value:
				func(key, value)

	def merge(self, dct, prefix=""):
		""" Merge values from dct with the values in the manipulator.

		Records not found is dct is left alone.

		@param dct: A dict where some keys are prefixed with "prefix".
		@param prefix: Only the nodes where the key is prefixed with
				this string is merged into the manipulator.
		"""
		self._merge(self.__setattr__, dct, prefix)

	def validate(self):
		""" Validate all values in the manipulator.
		@raise field.interface.FieldValidationError: If validation fails.
		"""
		for key in self.model:
			value = self.__getattr__(key)
			self.model[key].validate(key, value)

	def info_validate(self):
		""" Validate all values in the manipulator.
		@return: A list of L{field.interface.FieldValidationError}
				objects. If all values validates, the list is empty.
		"""
		errors = []
		for key in self.model:
			value = self.__getattr__(key)
			try:
				self.model[key].validate(key, value)
			except FieldValidationError, e:
				errors.append(e)
		return errors


	def __setattr__(self, name, value):
		""" Set the value of a field.
		@param name: The name of the field.
		@param value: The value.
		"""
		self._values[name] = value

	def __getattr__(self, name):
		""" Get the value of a field.
		@param name: The name of the field.
		@return: The stored value or the default value if not value
				is set for the field.
		"""
		return self._values.get(name, self.model[name].get_default())

	def __setitem__(self, name, value):
		""" Alias for L{__setattr__}. """
		self.__setattr__(name, value)
	def __getitem__(self, name):
		""" Alias for L{__getattr__}. """
		return self.__getattr__(name)


	#########################
	# from string

	def set_unicode(self, name, value):
		""" Set the value of a field using a string.
		The value is automatically converted to the correct type
		using the from_unicode method in the field.
		@param name: The name of the field.
		@param value: The value as a string.
		"""
		field = self.model[name]
		self.__setattr__(name, field.from_unicode(value))


	def unicode_merge(self, dct, prefix=""):
		""" Equal to L{merge} except it uses L{set_unicode} to set values. """
		self._merge(self.set_unicode, dct, prefix)




	def get_unicode(self, name):
		""" Get the value of a field as a unicode object.
		The value is automatically converted to unicode using
		the to_unicode method in the field.
		@param name: The name of the field.
		"""
		field = self.model[name]
		return field.to_unicode(self.__getattr__(name))


	def __str__(self):
		return self.__repr__()
	def __repr__(self):
		return "Manip <%r>" % self._values

	def __iter__(self):
		""" Iterate over all fields in the model, returning
		fieldname at each iteration. """
		return self.model.__iter__()

	def iteritems(self):
		""" Iterate over all fields in the model, returning
		(fieldname, value) pairs at each iteration. """
		for key in self.model:
			value = self.__getattr__(key)
			yield key, value

	def get_dict(self):
		""" Get values as a dict where field-name is key.
		If a value is not set the default value is used.
		"""
		d = {}
		for key, value in self.iteritems():
			d[key] = value
		return d

	def iterunicode(self):
		""" Iterate over all fields in the model, returning
		(fieldname, unicode-value) pairs at each iteration. """
		for key in self.model:
			value = self.get_unicode(key)
			yield key, value



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
