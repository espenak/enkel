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

""" Form parsing utilities.

@var QUERY_SEP: The separator separating variables in "query strings".
"""


from mimetypes import guess_type
from cStringIO import StringIO
from email.Parser import Parser
from urllib import unquote_plus
from tempfile import TemporaryFile

from utils import read_until



QUERY_SEP = "&"



class FormParseClientError(Exception):
	pass


class FormParams(object):
	""" A dictionary-like structure used to represent form
	"parameters".

	A form can contain I{one or more} of a parameter. To make this
	consistent, the object stores every parameter as a list of values.
	Values are added with L{add}, which does this automatically.

	Since this is a subclass of dict, you can also set parameters
	using __setitem__(param-name, value). But make sure the "value"
	is always a list. Note that __setitem__ should only be used if
	you for some reason cannot use L{add}.

	If you only use this module, you will probably only be interrested
	in the L{getfirst}, __getitem__ and get functions.


	Examples
	========
		>>> p = FormParams()

		>>> p.add(u"names", u"john")
		>>> p
		{u'names': [u'john']}
		>>> p.add(u"names", u"jack")
		>>> p
		{u'names': [u'john', u'jack']}

		>>> p.getfirst("names")
		u'john'

		>>> p.get(u"names")
		[u'john', u'jack']
		>>> p.get(u"doesnotexist", "default value")
		'default value'

		>>> p[u"names"] == p.get(u"names")
		True
		>>> p[u"doesnotexist"]
		Traceback (most recent call last):
		...
		KeyError: u'doesnotexist'

		>>> p(u"names") == p.getfirst(u"names")
		True

		>>> p.add(u"id", u"100")
		>>> [value for name, value in p.iterfirst()]
		[u'john', u'100']
	"""
	def __init__(self):
		self.val = {}

	def add(self, name, value):
		""" Add a value to a parameter.

		If the parameter already exists, append value to the parameter,
		if not create a new parameter.

		@raise ValueError: If name is not unicode or
				value is not unicode or L{MultipartFile}.

		@param name: The name of the parameter.
		@type value: unicode
		@param value: The value to add to the named parameter.
		"""
		if not isinstance(name, unicode):
			raise ValueError("'name' must be unicode")
		if not isinstance(value, (unicode, MultipartFile)):
			raise ValueError("'value' must be unicode or MultipartFile")
		if name in self.val:
			self.val[name].append(value)
		else:
			self.val[name] = [value]

	def __getitem__(self, name):
		""" Get the value of a parameter.
		@raise KeyError: If name is not a parameter.
		@return: A list of unicode objects.
		"""
		return self.val[name]

	def get(self, name, default=None):
		""" Get the value of a parameter.
		@return: A list of unicode objects or "default" of the
				parameter does not exist.
		"""
		return self.val.get(name, default)

	def getfirst(self, name, default=None):
		""" Get the first value for the requested parameter, or return
		the default value.

		@param name: The name of the parameter.
		@param default: Value to return if parameter is not found.
		@rtype: unicode
		@return: Described above.
		"""
		if name in self.val:
			return self.val[name][0]
		else:
			return default

	def __call__(self, name, default=None):
		""" Alias for L{getfirst}. """
		return self.getfirst(name, default)


	def __iter__(self):
		""" Iterate over all parameters yielding
		parameter-name's. """
		return self.val.__iter__()

	def iteritems(self):
		""" Iterate over all parameters yielding
		(name, value) pairs. """
		return self.val.iteritems()


	def iterfirst(self):
		""" Iterate over all parameters yielding
		(name, first-value) pairs. """
		for name, values in self.val.iteritems():
			yield name, values[0]


	def __contains__(self, name):
		return name in self.val

	def __repr__(self):
		return repr(self.val)
	def __str__(self):
		return str(self.val)


class Any(object):
	""" When you have data in more than one
	L{FormParams}, and do not care from which FormParams the data
	is retrived, you can use Any. It implements a subset of the
	functions provided by FormParams. """
	def __init__(self, *form_params):
		"""
		@param form_params: tuple of L{enkel.wansgli.formparse.FormParams}
				sorted in the preferred order.
		"""
		self.form_params = form_params

	def get(self, key, default=None):
		""" Get the list of parameters from the first FormParams
		containing "key", or return "default".
		"""
		for p in self.form_params:
			if key in p:
				return p[key]
		return default

	def getfirst(self, key, default=None):
		""" Get the first item in the list of parameters from the
		first FormParams containing "key", or return "default".
		"""
		v = self.get(key)
		if v == None:
			return default
		else:
			return v[0]

	def __call__(self, key, default=None):
		""" Alias for L{getfirst} """
		return self.getfirst(key, default)

	def __contains__(self, key):
		""" Check if "key" is in any of the FormParams. """
		for p in self.form_params:
			if key in p:
				return True
		else:
			return False

	def __repr__(self):
		b = ""
		for p in self.form_params:
			b += repr(p)
		return b


def parse_query_string(string, encoding):
	""" Parse a series of "field=value" pairs separated by L{QUERY_SEP}
	into a L{FormParams} instance.

	Example
	=======
		>>> p = parse_query_string("a=jeje&b=haha&a=10", "utf-8")
		>>> p
		{u'a': [u'jeje', u'10'], u'b': [u'haha']}
		>>> p("a")
		u'jeje'

	@param string: A url-encoded byte-string.
	@param encoding: The encoding to use to convert the string to
			unicode.
	@return: A L{FormParams} instance containing the result.
	"""
	d = FormParams()
	for x in string.split(QUERY_SEP):
		try:
			key, value = x.split("=", 1)
		except ValueError:
			continue
		else:
			value = unicode(unquote_plus(value), encoding)
			d.add(unicode(key, encoding), value)
	return d



class MultipartFile(object):
	""" Represents a "file" in a multipart POST request.

	@cvar DEFAULT_CONTENT_TYPE: The default content-type, used when no
			content-type is given, and mimetypes.guess_type cannot
			guess the type.

	@ivar filename: The filename sent to __init__.
	@ivar headers: The email.Message.Message object sent to __init__.
	@ivar content_type: The content-type of the file.
	"""
	DEFAULT_CONTENT_TYPE = "application/octet-stream"
	def __init__(self, fileobj, filename, headers):
		"""
		@param fileobj: A file-like object containing the file. The
				file pointer should be at the beginning of the file.
		@param filename: The filename of the file in fileobj.
		@param headers: A email.Message.Message object.
		"""
		self.fileobj = fileobj
		self.filename = filename
		self.headers = headers
		self.content_type = self.headers.get("content-type",
				guess_type(self.filename)[0] or self.DEFAULT_CONTENT_TYPE)

	def __del__(self):
		self.close()

	def __str__(self):
		""" Alias for L{read} with no size. """
		return self.read()

	def read(self, size=-1):
		return self.fileobj.read(size)
	def readline(self, size=-1):
		return self.fileobj.readline(size)
	def readlines(self):
		return self.fileobj.readlines()
	def close(self):
		if hasattr(self.fileobj, "close"):
			self.fileobj.close()





def parse_multipart(content_type, content_length, bodystream, encoding):
	""" Parse the body of a multipart form request as specified
	in rfc1867.

	Ignores case in header-names and supports both '\\n' and '\\r\\n'
	as a separator (but not a mix in the same bodystream).

	@param content_type: The content type header of the HTTP request.
	@param content_length: content-length as a long. "content_length"
			bytes are read from the bodystream, unless EOF is reached.
	@param bodystream: A file like object. Must have a read() method
			which supports the "size" parameter.
	@param encoding: The encoding to use when converting parameters
			to unicode. Files are not converted to unicode.

	@return: (files, var) Where both are L{FormParams}. C{files} contains
			L{MultipartFile} instances, and C{var} contains unicode objects.
	"""
	files = FormParams()
	var = FormParams()
	bytes_left = content_length
	extra = "--"

	# parse content-type
	try:
		ignore, boundary = content_type.split("=", 1)
	except ValueError:
		raise FormParseClientError(
			"multipart/form-data POST request without a boundary.")
	boundary = extra + boundary

	# detect separator
	bytes_read = len(boundary) + 1
	buf = bodystream.read(bytes_read)
	bytes_left -= bytes_read
	if buf[len(boundary)] == "\r":
		sep = "\r\n"
		bodystream.read(1) # also read \n
		bytes_left -= 1
	else:
		sep = "\n"


	rest = sep
	while(True):

		# extract header
		ostream = StringIO()
		bytes_read, success, rest = read_until(
				bodystream, ostream, sep+sep, before=rest,
				maxread=bytes_left)
		bytes_left -= bytes_read
		if not success:
			break
		headers = Parser().parsestr(
				ostream.getvalue()[len(sep):], headersonly=True)

		# parse content-disposition header
		try:
			x = headers["content-disposition"].split(";")
		except AttributeError:
			continue # ignore blocks without a content-disposition header
		filename = None
		name = None
		for param in x[1:]:
			p = param.split("=", 1)
			if not len(p) == 2:
				continue # ignore invalid params
			key = p[0].strip()
			val = p[1][1:-1]
			if key == "name":
				name = val
			elif key == "filename":
				filename = val
		if not name:
			break

		# parse body into buffer
		if filename:
			ostream = TemporaryFile()
		else:
			ostream = StringIO()
		bytes_read, success, rest = read_until(
				bodystream, ostream, sep+boundary, before=rest,
				maxread=bytes_left)
		bytes_left -= bytes_read
		if not success:
			break

		# add to correct container
		if filename:
			ostream.seek(0)
			v = MultipartFile(ostream, filename, headers)
			files.add(unicode(name, encoding), v)
		else:
			var.add(
				unicode(name, encoding),
				unicode(ostream.getvalue(), encoding))

	return (files, var)



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from testhelpers import run_suite
	run_suite(suite())
