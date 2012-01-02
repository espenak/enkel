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

""" fast XML writer. """

from xml.sax.saxutils import escape, quoteattr


class XmlWriter(object):
	""" A fast xml writer specialized only for creating xml
	output.


	Unicode handling
	================
		Everything sent into the writer is converted to unicode.
		This is done using the unicode() function with encoding="ascii".
		So if you want to insert anything outside of "ascii" you must
		send in unicode objects.


	Examples
	========

		Very simple
		-----------
		>>> w = XmlWriter()
		>>> w.start_element("html")
		>>> w.start_element("body")
		>>> w.text_node("test")
		>>> print w.create()
		<html><body>test</body></html>


		A bit more advanced
		-------------------

		>>> w = XmlWriter(pretty=True)
		>>> w.pi("xml", version="1.0", encoding="utf-8")
		>>> w.pi("xml-stylesheet", type="text/xsl", href="test.xsl")
		>>> w.start_element("person")
		>>> w.start_element("name")
		>>> w.text_node("John")
		>>> w.end_element()
		>>> w.empty_element("birth", attrdict={"sec-after-midnight": "25"},
		... 	year="1920", month="12", day="24")
		>>> w.empty_element("test", title="testing")
		>>> w.end_element()
		>>> print w.create()
		<?xml version="1.0" encoding="utf-8"?>
		<?xml-stylesheet href="test.xsl" type="text/xsl"?>
		<BLANKLINE>
		<person>
		   <name>
		John
		   </name>
		   <birth sec-after-midnight="25" month="12" day="24" year="1920"/>
		   <test title="testing"/>
		</person>


		>>> w = XmlWriter(pretty=True)
		>>> w.pi_raw("xml-stylesheet", "type='text/xsl' href='xslt/xhtml/admin.xsl'")
		>>> w.start_element("html")
		>>> w.start_element("body", bgcolor="red")
		>>> w.empty_element("div", id="one")
		>>> w.start_element("div", id="two")
		>>> w.text_node("10 < 20 but 30 > 20")
		>>> w.raw_node("<div id='three'/>")
		>>> w.end_element(-1)
		>>> print w.create()
		<?xml-stylesheet type='text/xsl' href='xslt/xhtml/admin.xsl'?>
		<BLANKLINE>
		<html>
		   <body bgcolor="red">
		      <div id="one"/>
		      <div id="two">
		10 &lt; 20 but 30 &gt; 20
		<div id='three'/>
		      </div>
		   </body>
		</html>
		"""
	def __init__(self, oldhtmlcomp=False, pretty=False, indent="   "):
		"""
		@param oldhtmlcomp: If True, add a whitespace before "/>" on
				all stand-alone tags, for compatibility with old
				html parsers.
		"""
		self.buf = []
		self.open_elements = []
		self.pretty = pretty
		self._indent = ""
		self.indent = indent
		if oldhtmlcomp:
			self.single_spatt = "<%s />"
		else:
			self.single_spatt = "<%s/>"

	def _to_unicode(self, obj):
		if isinstance(obj, unicode):
			return obj
		else:
			return unicode(obj, "ascii")

	def _gen_element(self, element_name, attrs):
		attrdict = attrs.pop("attrdict", None)
		if attrdict:
			if isinstance(attrdict, dict):
				attrs.update(attrdict)
			else:
				attrs["attrdict"] = attrdict
		e = [self._to_unicode(element_name)]
		for attrelement_name, attrvalue in attrs.iteritems():
			e.append("%s=%s" % (attrelement_name, quoteattr(self._to_unicode(attrvalue))))
		return e

	def start_element(self, element_name, **attrs):
		"""
		@param element_name: The element_name of the element.
		@param attrs: A dict of attributes. If this dict has
				a node with key "attrdict", this dict will update
				attrs before attributes are added (see examples above).
		"""
		e = self._gen_element(element_name, attrs)
		elm = "<%s>" % " ".join(e)
		if self.pretty:
			elm = "\n" + self._indent + elm
			self._indent += self.indent
		self.buf.append(elm)
		self.open_elements.append(element_name)

	def end_element(self, count=1):
		""" Close element(s).
		@param count: The number of elements to close. Close all
				open elements if count is -1.
		"""
		if count == -1:
			count = len(self.open_elements)
		for i in xrange(count):
			element_name = self.open_elements.pop()
			elm = "</%s>" % element_name
			if self.pretty:
				self._indent = self._indent[:-len(self.indent)]
				elm = "\n" + self._indent + elm
			self.buf.append(elm)

	def empty_element(self, element_name, **attrs):
		""" Create a element with no child-nodes.
		Paremeters are the same as for L{start_element}.
		"""
		e = self._gen_element(element_name, attrs)
		e = self.single_spatt % " ".join(e)
		if self.pretty:
			e = "\n" + self._indent + e
		self.buf.append(e)

	def text_element(self, element_name, text, **attrs):
		""" Create a element with a textnode as only child.
		Paremeters are the same as for L{start_element} except
		for "text" which means the same as in L{text_node}.
		"""
		self.start_element(element_name, **attrs)
		self.text_node(text)
		self.end_element()


	def indent_text(self, text):
		""" Used by L{text_node} to indent the text when
		L{__init__} is invoked with the B{pretty} parameter.
		This implementation only returns the text without
		any changes, but you might wish to override it
		to provide indentation of text nodes.
		"""
		return text

	def text_node(self, text):
		""" Create a text-node.
		@param text: The contents of the text-node. It is escaped
				using xml.saxutils.escape.
		"""
		elm = self.indent_text(escape(self._to_unicode(text)))
		if self.pretty:
			elm = "\n" + elm
		self.buf.append(elm)

	def raw_node(self, rawdata):
		""" Add raw data to the xml document.
		This is the same as L{text_node} except the data is not escaped.
		@param rawdata: The data.
		"""
		elm = self._to_unicode(rawdata)
		if self.pretty:
			elm = "\n" + elm
		self.buf.append(elm)

	def pi_raw(self, target, body):
		""" Add a processing instruction.
		@param target: The target application.
		@param body: The data sent to the application.
		"""
		pi = "<?%s %s?>" % (target, self._to_unicode(body))
		if self.pretty:
			pi = pi + "\n"
		self.buf.append(pi)

	def pi(self, target, **attrs):
		""" Add a processing instruction.
		@param target: The target application.
		@param attrs: Works just like in L{start_element}.
		"""
		e = self._gen_element(target, attrs)
		pi = "<?%s?>" % " ".join(e)
		if self.pretty:
			pi = pi + "\n"
		self.buf.append(pi)

	def create(self, autoend=True):
		""" Create XML from the input.
		@param autoend: If True, run L{end_element(-1)} if
				there are any open elements.
		@return: A unicode object containing the resulting xml.
		"""
		if autoend and len(self.open_elements) > 0:
			self.end_element(-1)
		return "".join(self.buf)


def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
