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

from xml.sax.saxutils import escape, quoteattr
from cStringIO import StringIO

from enkel.model import ds
from enkel.model.field.base import String, Text, Bool
from enkel.model.formgen import Form
from enkel.xmlutils.writer import XmlWriter


class Form(Form):
	""" XHTML form generator.

	@note: The output is defined in form.rng.

	@ivar css_class: The css class used on the div's surrounding
			every field.
	@ivar method: The http method used to send the form.
	@ivar oldhtmlcomp: Insert a whitspace before all standalone
			xml tag endings to be compatible with very old
			html browsers.
	@ivar pretty: Make readable xml. Inserts extra whitespace,
			which might lead to problems with certain (buggy)
			parsers.
	@ivar xmlns: The xml namespace used on the root tag of the
			result xml node. If None, no xmlns is used.
	"""

	css_class = "form_field"
	method = "post"
	oldhtmlcomp = False
	pretty = False
	xmlns = "http://www.w3.org/1999/xhtml"

	def start_form(self):
		args = {"method": "post"}
		if self.xmlns:
			args["xmlns"] = self.xmlns
		if self.id:
			args["id"] = self.id

		if self.method == "multipart":
			args["enctype"] = "multipart/form-data"
		elif self.method == "get":
			args["method"] = "get"

		self.w.start_element("form", action=self.action,
				**args)

	def start_group(self, title):
		if title:
			self.w.start_element("fieldset")
			self.w.start_element("legend")
			self.w.text_node(title)
			self.w.end_element()


	def handle_field_body(self, prefix, fieldname, field, value,
				uvalue, meta, display):
		commonattr = dict(name=prefix+fieldname, id=prefix+fieldname)

		readonly = display.get("readonly")
		if readonly:
			if isinstance(field, ds.DatasourceField):
				raise ValueError(
					"%s: DatasourceField cannot be readonly." % fieldname)
			commonattr["disabled"] = "disabled"

		if isinstance(field, ds.DatasourceField):
			datasource = field.datasource

			size = 0
			opt = XmlWriter(oldhtmlcomp=self.oldhtmlcomp,
					pretty=self.pretty)
			for uval, label in datasource.ds_iter_unicode():
				attr = {}
				if \
						(isinstance(field, ds.Many) and\
							uval in uvalue) or\
						(isinstance(field, ds.One) and\
							uval == uvalue):
					attr["selected"] = "selected"

				attr["value"] = uval
				opt.start_element("option", **attr)
				opt.text_node(label)
				opt.end_element()
				size += 1

			attr = commonattr.copy()
			if isinstance(field, ds.Many):
				attr["multiple"] = "multiple"
			if size > 10:
				size = 10
			self.w.start_element("select", size=str(size), **attr)
			self.w.raw_node(opt.create())
			self.w.end_element()


		else:
			if isinstance(field, String):
				maxlength = field.maxlength
				if maxlength > 50:
					self.w.start_element("textarea", cols="70", rows="3",
							**commonattr)
					self.w.text_node(uvalue)
					self.w.end_element()
				else:
					self.w.empty_element("input",
							type = "text",
							maxlength = str(maxlength),
							value = uvalue,
							**commonattr)

			elif isinstance(field, Text):
				self.w.start_element("textarea", cols="70", rows="12",
						**commonattr)
				self.w.text_node(uvalue)
				self.w.end_element()

			elif isinstance(field, Bool):
				attr = commonattr.copy()
				if value == True:
					attr["checked"] = "checked"
				self.w.empty_element("input",
						type = "checkbox",
						value = "yes",
						**attr)

			else:
				self.w.empty_element("input",
						type = "text",
						value = uvalue,
						**commonattr)


	def handle_field(self, prefix, fieldname, field, value,
			uvalue, meta, display):

		if display.get("hidden"):
			if isinstance(field, ds.Many):
				values = uvalue
			else:
				values = [uvalue]
			for v in values:
				self.w.empty_element("input",
						type = "hidden",
						value = v,
						name = prefix+fieldname)
			return

		self.w.start_element("div", attrdict={"class": self.css_class})

		self.w.start_element("label", attrdict={"for": prefix+fieldname})
		self.w.text_node(meta.get("label", fieldname))
		self.w.end_element()

		self.handle_field_body(prefix, fieldname, field, value,
				uvalue, meta, display)

		self.w.start_element("div",
			attrdict={"class": self.css_class+"_shorthelp"})
		self.w.text_node(meta.get("shorthelp", ""))
		self.w.end_element()

		error = display.get("error")
		if error:
			self.w.start_element("div",
				attrdict={"class": self.css_class+"_error"})
			self.w.text_node(error)
			self.w.end_element()

		self.w.end_element() # </div>


	def end_group(self, title):
		if title:
			self.w.end_element() # </fieldset>

	def end_form(self):
		self.w.empty_element("input", type="submit",
				value=self.submit_label)
		self.w.end_element() # </form>


	def create(self):
		self.w = XmlWriter(oldhtmlcomp=self.oldhtmlcomp,
				pretty=self.pretty)
		super(Form, self).create()
		return self.w.create()
