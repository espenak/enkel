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
Validation of various exml languages.

NOTE
====
	When the documentation below refers to a "<filename>.rng"
	it refers to a file in enkel/rngdata/.

WARNING
=======
	This module depends on the B{lxml} library.
"""

from os.path import join
from lxml import etree

from enkel.rngdata import RNGDIR
from enkel.model.field.xmlf import LxmlFieldValidationError


def validate_inline_field(fieldname, xml, offset):
	""" L{enkel.model.field.xmlf.XmlField} compatible validation
	agains "inline.rng".

	>>> from enkel.model.field.xmlf import XmlField
	>>> from info import XMLNS_MARKUP as ns
	>>> f = XmlField(validate=validate_inline_field)
	>>> xml = u"<inline xmlns='%s'>hello</inline>" % ns
	>>> f.validate("f", xml)
	"""
	try:
		validate_inline(etree.XML(xml))
	except etree.LxmlError, e:
		raise LxmlFieldValidationError(fieldname, xml, offset, e)


def validate_inline(xml):
	""" Validate a xml document against "inline.rng".

	Examples
	========
		>>> from lxml.etree import parse, XML, DocumentInvalid
		>>> from cStringIO import StringIO
		>>> from info import XMLNS_MARKUP as ns

		>>> doc = "<inline xmlns='%s'><em>hello</em></inline>" % ns
		>>> validate_inline(XML(doc))
		>>> validate_inline(parse(StringIO(doc)))

		>>> doc = "<inline xmlns='%s'><x/>hello</inline>" % ns
		>>> try:
		... 	validate_inline(XML(doc))
		... except DocumentInvalid, e:
		... 	print "Invalid document"
		Invalid document


	@raise lxml.etree.DocumentInvalid: If the document does
			not validate.
	@raise lxml.etree.XMLSyntaxError: If the document is not
			valid xml.
	@note: Might raise other exceptions. The lxml docs do not
			give a lot of exception information.
	@param xml: A lxml.etree.ElementTree object.
	"""
	rng_file = join(RNGDIR, "inline-standalone.rng")
	rng_doc = etree.parse(rng_file)
	rng = etree.RelaxNG(rng_doc)
	rng.assertValid(xml)


def validate_section_field(fieldname, xml, offset):
	""" L{enkel.model.field.xmlf.XmlField} compatible validation
	agains "section.rng".

	>>> from enkel.model.field.xmlf import XmlField
	>>> from info import XMLNS_MARKUP as ns
	>>> f = XmlField(validate=validate_section_field)
	>>> xml = u"<section xmlns='%s'><h>hello</h></section>" % ns
	>>> f.validate("f", xml)
	"""
	try:
		validate_section(etree.XML(xml))
	except etree.LxmlError, e:
		raise LxmlFieldValidationError(fieldname, xml, offset, e)

def validate_section(xml):
	""" Validate a xml document against "section.rng".
	Parameters and excetions are the same as
	L{validate_inline}.
	"""
	rng_file = join(RNGDIR, "section.rng")
	rng_doc = etree.parse(rng_file)
	rng = etree.RelaxNG(rng_doc)
	rng.assertValid(xml)


def validate_markup_field(fieldname, xml, offset):
	""" L{enkel.model.field.xmlf.XmlField} compatible validation
	agains "markup.rng".

	>>> from enkel.model.field.xmlf import XmlField
	>>> from info import XMLNS_MARKUP as ns
	>>> f = XmlField(validate=validate_markup_field)
	>>> xml = u"<markup xmlns='%s'><p>hello</p></markup>" % ns
	>>> f.validate("f", xml)
	"""
	try:
		validate_markup(etree.XML(xml))
	except etree.LxmlError, e:
		raise LxmlFieldValidationError(fieldname, xml, offset, e)

def validate_markup(xml):
	""" Validate a xml document against "markup.rng".
	Parameters and excetions are the same as
	L{validate_inline}.
	"""
	rng_file = join(RNGDIR, "markup.rng")
	rng_doc = etree.parse(rng_file)
	rng = etree.RelaxNG(rng_doc)
	rng.assertValid(xml)



def validate_formsection(xml):
	""" Validate a document agains "formsection.rng".
	Parameters and excetions are the same as
	L{validate_inline}.
	"""
	rng_file = join(RNGDIR, "formsection.rng")
	rng_doc = etree.parse(rng_file)
	rng = etree.RelaxNG(rng_doc)
	rng.assertValid(xml)


def validate_form(xml):
	""" Validate a document agains "form-standalone.rng".
	Parameters and excetions are the same as
	L{validate_inline}.
	"""
	rng_file = join(RNGDIR, "form-standalone.rng")
	rng_doc = etree.parse(rng_file)
	rng = etree.RelaxNG(rng_doc)
	rng.assertValid(xml)




def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
