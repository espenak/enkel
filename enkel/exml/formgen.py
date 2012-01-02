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

from enkel.model.field.base import *
from enkel.model.formgen import Form
from enkel.model.ds import One, Many, DatasourceField
from enkel.xmlutils.writer import XmlWriter

from info import XMLNS_FORM


class Form(Form):
	""" EXML Form generator.
	@ivar xmlns: The xml namespace used on the root tag of the
			result xml node. Defaults to L{info.XMLNS_FORM}.
			If None, no xmlns is used.
	@ivar pretty: Make readable xml. Inserts extra whitespace,
			which might lead to problems with certain (buggy)
			parsers.
	"""
	xmlns = XMLNS_FORM
	pretty = False
	def start_form(self):
		kw = {}
		if self.xmlns:
			kw["xmlns"] = self.xmlns
		if self.id:
			kw["id"] = self.id

		self.w.start_element("form",
				action=self.action, method=self.method,
				submit_label=self.submit_label, **kw)


	def start_group(self, title):
		self.w.start_element("group", title=title)

	def handle_field(self, prefix, fieldname, field, value,
			uvalue, meta, display):

		if display.get("hidden"):
			if isinstance(field, Many):
				values = uvalue
			else:
				values = [uvalue]
			for v in values:
				self.w.start_element("hidden", id=prefix+fieldname)
				self.w.text_node(v)
				self.w.end_element()
			return

		readonly = display.get("readonly")
		if readonly:
			if isinstance(field, DatasourceField):
				raise ValueError(
					"%s: DatasourceField cannot be readonly." % fieldname)

		name = None
		for ttype, name in (
			(String, "string"),
			(Int, "int"),
			(Long, "long"),
			(Float, "float"),
			(Text, "text"),
			(Date, "date"),
			(DateTime, "datetime"),
			(Time, "time"),
			(Many, "many"),
			(One, "one"),
			(Bool, "bool")
		):
			if isinstance(field, ttype):
				break
		if not name:
			raise ValueError(
"""All form fields must be instances of one of the base field
types defined in enkel.model.field.base. Or one of the two datasource
fields defined in enkel.model.ds. """)
		elif name == "string" and \
				field.maxlength > field.LONG_STRING:
			name = "longstring"
		elif readonly:
			name = "readonly"

		if field.required:
			required = "yes"
		else:
			required = "no"

		self.w.start_element(name, # start field element
				id = prefix + fieldname,
				typehint = field.__class__.__name__,
				required = required)

		self.w.start_element("label")
		self.w.text_node(meta.get("label", fieldname))
		self.w.end_element()

		self.w.start_element("tooltip")
		self.w.text_node(meta.get("shorthelp", ""))
		self.w.end_element()

		if isinstance(field, One):
			datasource = field.datasource
			self.w.start_element("onevalue")
			for val, label in datasource.ds_iter_unicode():
				if val == uvalue:
					name = "sel_item"
				else:
					name = "item"
				self.w.start_element(name, value=val)
				self.w.text_node(label)
				self.w.end_element()
			self.w.end_element()

		elif isinstance(field, Many):
			datasource = field.datasource
			self.w.start_element("manyvalue")
			for val, label in datasource.ds_iter_unicode():
				if val in uvalue:
					name = "sel_item"
				else:
					name = "item"
				self.w.start_element(name, value=val)
				self.w.text_node(label)
				self.w.end_element()
			self.w.end_element()

		else:
			self.w.start_element("value")
			self.w.text_node(uvalue)
			self.w.end_element()

		error = display.get("error")
		if error:
			self.w.start_element("error")
			self.w.text_node(error)
			self.w.end_element()

		self.w.end_element() # end field element


	def end_group(self, title):
		self.w.end_element()

	def end_form(self):
		self.w.end_element()


	def create(self):
		self.w = XmlWriter(pretty=self.pretty)
		super(Form, self).create()
		return self.w.create()
