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

""" Helpers for working with models. """

import ds, data



def error_handler(e):
	""" Default error handler for L{ModelData.validate}.
	@param e: A L{field.interface.FieldValidationError}.
	@return: e.long_message.
	"""
	return e.long_message


class ModelData(object):
	""" Models are defined as dicts, manipulated with Manip's,
	made presentable with meta-data (also dicts. This class
	helps you work with all these things as a whole.

	@ivar manip: See the I{manip} parameter to L{__init__}.
	@ivar meta: See the I{meta} parameter to L{__init__}.
	@ivar display: See the I{display} parameter to L{__init__}.
	"""
	def __init__(self, manip, meta={}, display={}):
		"""
		@param manip: A L{data.Manip} object.
		@param meta: A dict containing meta-data about the fields
				in the model. It must be a dict containing dicts
				grouped by fieldname like this:

				>>> from field.base import String, Int
				>>> model = dict(
				... 	name = String(),
				... 	age = Int()
				... )
				>>> meta = dict(
				... 	name = {
				... 		"label": "Your name",
				... 		"shorthelp": "yes! your name;)"},
				... 	age = {
				... 		"shorthelp": "A whole number."}
				... )

				Which meta-names you should use are up to the
				module using the meta information. But if you create
				a module using meta-information you should use these
				names (if you need the info):
					- B{label}: A short label for the field.
					- B{shorthelp}: Short help. Only a single sentence
					  or a couple of very short sentences.
					- B{longhelp}: A longer help text.
		@param display: A dict containing diplay infomation for
				the model. Same syntax and rules as for "meta",
				but reccomended names are:
					- B{readonly}: The field is read-only.
					- B{hidden}: The field only carries data and is
					  not visible to the user.
					- B{error}: A error message.
		"""
		self.manip = manip
		self.meta = meta
		self.display = {}

	def validate(self, error_handler=error_handler):
		""" Validate L{manip}.
		Run L{manip}.info_validate() and place the result in
		L{display}[fieldname]["error"].

		@param error_handler: A error handling callable.
				Defaults to L{error_handler}.
		"""
		for e in self.manip.info_validate():
			if not self.display.get(e.fieldname):
				self.display[e.fieldname] = {}
			self.display[e.fieldname]["error"] = error_handler(e)



def forminput_to_manip(model, formparams, prefix=""):
	""" Convert forminput into a L{data.Manip}.

	Example
	=======
		>>> from enkel.wansgli.apputils import FormInput
		>>> from field.base import String, Int

		>>> model = dict(name=String(), id=Int(), x=Int())
		>>> env = dict(
		... 	QUERY_STRING = "name=john&id=8812&x=10&x=20",
		... 	REQUEST_METHOD = "GET"
		... )
		>>> f = FormInput(env)
		>>> forminput_to_manip(model, f)
		Manip <{'x': 10, 'id': 8812, 'name': u'john'}>

		>>> env["QUERY_STRING"] = "a_name=john&a_id=8812&a_x=10"
		>>> f = FormInput(env)
		>>> forminput_to_manip(model, f, "a_")
		Manip <{'x': 10, 'id': 8812, 'name': u'john'}>


	@type model: dict
	@param model: The model for the manipulator-
	@type formparams: L{enkel.wansgli.formparse.FormParams}
	@param formparams: L{enkel.wansgli.formparse.FormParams} object or a
			object with the same same interface. This includes:
				- L{enkel.wansgli.apputils.FormInput}
				- L{enkel.wansgli.apputils.FormInput.GET}
				- L{enkel.wansgli.apputils.FormInput.POST}
				- L{enkel.wansgli.apputils.FormInput.any}
				- L{enkel.wansgli.apputils.FormInput.files}

	"""
	m = data.Manip(model)
	for name, field in model.iteritems():
		if isinstance(field, ds.Many):
			m.set_unicode(name, formparams.get(prefix+name, []))
		else:
			m.set_unicode(name, formparams.getfirst(prefix+name, u""))
	return m



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
