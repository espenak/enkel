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


r""" Automatic form generation using the model interface.

Example
=======
	This example uses exml form format. But you can use any
	form generator. For example: L{enkel.xhtml.formgen}.

	>>> from enkel.model import data
	>>> from enkel.model.formgen import AutoSort
	>>> from enkel.model.util import ModelData
	>>> from enkel.model.field.base import String, Int
	>>> from enkel.exml.formgen import Form


	A very simple example
	---------------------

	>>> aboutmodel = dict(
	... 	name = String(),
	... 	age = Int()
	... )
	>>> aboutmanip = data.Manip(aboutmodel)

	>>> form = Form("http://www.example.com/submit", "Submit form")
	>>> form["ab_"] = ModelData(aboutmanip)


	Setting default values
	----------------------

	>>> aboutmanip.name = "John"
	>>> aboutmanip.age = 25


	Labels and tooltip
	------------------

	>>> aboutmeta = {
	... 	"name": {
	... 		"label": "Name",
	... 		"shorthelp": "You name here"},
	... 	"age": {
	... 		"label": "Your age"}
	... }
	>>> form["ab_"].meta = aboutmeta


	Hidden and read-only fields
	---------------------------
	>>> form["ab_"].display = {
	... 	"age": {
	... 		"hidden": True},
	... 	"name": {
	... 		"readonly": True}
	... }


	Setting errors
	--------------

	You can just set an error message directly in the meta dict
	like this:

	>>> form["ab_"].display["age"]["error"] = "This in an error:("

	But normally you will validate the Manip and dump the
	result like this:

	>>> aboutmanip.age = "twentyfive"
	>>> form["ab_"].validate()

	You can also add your own error handler.

	>>> def handle_error(e):
	... 	return "an error occurred"
	>>> form["ab_"].validate(handle_error)
	>>> form["ab_"].display["age"]["error"]
	'an error occurred'


	More than one model in the form
	-------------------------------

	>>> emailmodel = dict(
	... 	subject = String(20),
	... 	to = String(50),
	... 	body = String(200)
	... )
	>>> emailmanip = data.Manip(emailmodel)
	>>> form["em_"] = ModelData(emailmanip)


	Custom layout
	-------------

	We can mix and group fields however we want.

	>>> form.set_layout(
	... 	("ab_","name"), ("em_","to"),
	... 	FormGroup("A group",
	... 		("em_","body"), ("ab_","subject"), ("ab_","name"))
	... )

	This is the default layout:

	>>> form.set_layout(AutoSort(
	... 	em_ = emailmodel,
	... 	ab_ = aboutmodel
	... ))

	We can also mix auto-sorting and custom layout..

	>>> form.set_layout(
	... 	("ab_","name"), ("ab_","age"),
	... 	FormGroup(u"Email",
	... 		*AutoSort(em_ = emailmodel))
	... )
"""

from heapq import heappush, heappop



class _AutoSortField(object):
	def __init__(self, prefix, fieldname, field):
		self.prefix = prefix
		self.fieldname = fieldname
		self.field = field

	def __cmp__(self, other):
		return cmp(self.field, other.field)



class AutoSort(object):
	""" Autosort form field. """
	def __init__(self, *fields, **models):
		"""
		@param fields: The fields to sort as (prefix, fieldname)
				tuples. If no fields are given, the list defaults
				to all fields in all the models.
		@param models: Dict of models with prefix as key.
		"""
		if len(fields) == 0:
			fields = []
			for prefix, model in models.iteritems():
				fields.extend(
					[(prefix, fieldname) for fieldname in model.iterkeys()])

		self.heap = []
		for prefix, fieldname in fields:
			field = models[prefix][fieldname]
			heappush(self.heap, _AutoSortField(prefix, fieldname, field))

	def __iter__(self):
		""" Yields (prefix, fieldname) tuples in order. """
		while self.heap:
			f = heappop(self.heap)
			yield f.prefix, f.fieldname


class FormGroup(object):
	def __init__(self, title, *layout):
		"""
		@type title: unicode.
		@param title: The title of the group.
		@param layout: A list of (prefix, fieldname) tuples and
				L{FormGroup} objects.
		"""
		self.title = title
		self.layout = layout



class Form(object):
	""" Form modelling system.

	Parsing
	=======
		The sytem uses a SAX like interface to parse the form.
		So all a implementation has to do to create custom forms
		is to subclass and implement the "parsing interface".

	The parsing interface
	=====================
		- L{start_form}
		- L{start_group}
		- L{handle_field}
		- L{end_group}
		- L{end_form}
	"""
	def __init__(self, action, submit_label, id=None,
				method="multipart"):
		"""
		@param action: The action(a URL) of the form.
		@param submit_label: The label of the submit "button".
		@param id: A unique id for the form.
		@param method: 'post', 'get' or 'multipart'. 'post' and
				'get' produce a form sending parameters using
				the HTTP method with the same same. 'multipart'
				results in a 'multipart/form-data' encoded
				HTTP POST request.
		"""
		self.action = action
		self.submit_label = submit_label
		self.layout = []
		self.id = id
		self.method = method
		self._data = {}


	def __setitem__(self, prefix, modeldata):
		"""
		@param prefix: The prefix identifying the modeldata.
		@param modeldata: A L{util.ModelData} object.
		"""
		self._data[prefix] = modeldata

	def __getitem__(self, prefix):
		"""
		@raise KeyError: If no modeldata with this prefix exists.
		@param prefix: The prefix identifying the modeldata.
		@return: A L{util.ModelData} object.
		"""
		return self._data[prefix]


	def set_layout(self, *layout):
		""" Set the layout.
		@param layout: A list of (prefix, fieldname) tuples and
				L{FormGroup} objects.
		"""
		self.layout = layout


	def _create_layout(self, layout):
		for item in layout:
			if isinstance(item, FormGroup):
				self._create_group(item)
			else:
				prefix, fieldname = item
				data = self[prefix]
				self.handle_field(
					prefix, fieldname,
					field = data.manip.model[fieldname],
					value = data.manip[fieldname],
					uvalue = data.manip.get_unicode(fieldname),
					meta = data.meta.get(fieldname, {}),
					display = data.display.get(fieldname, {})
				)

	def _create_group(self, group):
		self.start_group(group.title)
		self._create_layout(group.layout)
		self.end_group(group.title)

	def create(self):
		""" Create the form and return the result.
		@return: A unicode object containing the form.
		"""
		if not self.layout:
			l = {}
			for prefix, data in self._data.iteritems():
				l[prefix] = data.manip.model
			self.set_layout(*AutoSort(**l))
		self.start_form()
		self._create_layout(self.layout)
		self.end_form()


	def start_form(self):
		""" Invoked at the beginning of the form (first in L{create}). """
		raise NotImplementedError()

	def start_group(self, title):
		""" Invoked at the start of a group.
		@param title: The title of the group or None if no title.
		"""
		raise NotImplementedError()

	def handle_field(self, prefix, fieldname, field, value,
			uvalue, meta, display):
		""" Invoked every time a form-field in encountered.
		@param prefix: The prefix for the ModelData containing the field.
		@param fieldname: The name of the field in the model.
		@param field: L{field.interface.Field} object.
		@param value: The raw value of the field.
		@param uvalue: The unicode value of the field.
		@param meta: The meta dict for the field. Meta-dicts are
				described in L{util.ModelData.__init__}. Used keys
				are "label" and "shorthelp" just as they are described
				in ModelData.
		@param display: The display dict for the field. Display-dicts are
				described in L{util.ModelData.__init__}. Used keys
				are "readonly", "error" and "hidden" just as they
				are described in ModelData.
		"""
		raise NotImplementedError()

	def end_group(self, title):
		""" Invoked at the end of every group.
		@param title: The title of the group or None if no title.
		"""
		raise NotImplementedError()

	def end_form(self):
		""" Invoked at the end of the form (last in L{create}). """
		raise NotImplementedError()



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
