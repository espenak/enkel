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

""" Simplified form input parsing similare to cgi.FieldStorage
(uses enkel.wansgli.formparse) """


from formparse import parse_query_string, parse_multipart,\
		FormParams, Any


class FormInputClientError(Exception):
	def __init__(self, msg):
		msg = "Client bug/error: " + msg
		FormInputError.__init__(self, msg)


class FormInput(object):
	"""
	>>> from cStringIO import StringIO
	>>> from enkel.wansgli.apptester import encode_multipart


	Using GET method
	================
		>>> env = dict(
		... 	QUERY_STRING = "name=john&id=8812&x=10&x=20",
		... 	REQUEST_METHOD = "GET"
		... )
		>>> f = FormInput(env)
		>>> f.GET
		{u'x': [u'10', u'20'], u'name': [u'john'], u'id': [u'8812']}
		>>> f.POST
		{}
		>>> f.GET.get("x")
		[u'10', u'20']
		>>> f.GET("x")
		u'10'
		>>> f.GET("x") == f.GET.getfirst("x")
		True


	Using POST method
	=================
		>>> q = "a=10&a=20&name=peter"
		>>> env = dict()
		>>> env["REQUEST_METHOD"] = "POST"
		>>> env["wsgi.input"] = StringIO(q)
		>>> env["CONTENT_LENGTH"] = len(q)
		>>> env["CONTENT_TYPE"] = "application/x-www-form-urlencoded"

		>>> f = FormInput(env)
		>>> f.POST
		{u'a': [u'10', u'20'], u'name': [u'peter']}
		>>> f.POST.get("name")
		[u'peter']
		>>> f.POST("a")
		u'10'


	any and default
	===============
		>>> env = dict(
		... 	QUERY_STRING = "name=john&id=8812&x=10&x=20",
		... 	REQUEST_METHOD = "GET"
		... )

		any is used if you do not care about the method.

		>>> f = FormInput(env)
		>>> f.any
		{u'x': [u'10', u'20'], u'name': [u'john'], u'id': [u'8812']}{}
		>>> f.any("name")
		u'john'
		>>> f.any.getfirst("x")
		u'10'

		defaults can be used just like with dict.get()

		>>> f.any("does not exist", 1000)
		1000


	Testing multipart request
	=========================
		>>> params = [
		... 	("myfile", "this is a test", "myfile.png", "image/png"),
		... 	("x", "10"),
		... 	("y", "20", "y1.txt"),
		... 	("y", "30", "y2.txt")
		... ]
		>>> boundary, q = encode_multipart(params)

		>>> env = dict()
		>>> env["REQUEST_METHOD"] = "POST"
		>>> env["wsgi.input"] = StringIO(q)
		>>> env["CONTENT_LENGTH"] = len(q)
		>>> env["CONTENT_TYPE"] = "multipart/form-data; boundary=%s" % boundary

		>>> f = FormInput(env)

		>>> f.files.getfirst("myfile").read()
		'this is a test'
		>>> f.files.getfirst("myfile").filename
		'myfile.png'
		>>> f.files("myfile").content_type
		'image/png'


	Testing unicode support
	=======================
		Note that we specify encoding="utf-8", but this is not
		really required as utf-8 is the default.

		>>> env = {
		... 	"REQUEST_METHOD": "GET",
		... 	"QUERY_STRING": u"name=\u00e5ge".encode("utf-8")
		... }
		>>> f = FormInput(env, encoding="utf-8")
		>>> f.GET.getfirst("name") == u"\u00e5ge"
		True


	@ivar GET: L{enkel.wansgli.formparse.FormParams} object containing
			all variables retrived from a GET request. All values
			are unicode strings.
	@ivar POST: L{enkel.wansgli.formparse.FormParams} object containing all
			variables retrived from a POST request. All values are
			unicode strings.
	@ivar any: L{Any} object containing all variables
			retrived from a POST or GET request. All values are strings.
	@ivar files: L{enkel.wansgli.formparse.FormParams} object containing all
			files retrived from a multipart POST request. All values are
			L{enkel.wansgli.formparse.MultipartFile} objects.
	"""

	def __init__(self, env, encoding="utf-8"):
		"""
		@param env: A wsgi environ dict.
		@param encoding: The expected input encoding.
		"""
		self.env = env
		self.method = env["REQUEST_METHOD"]
		self.encoding = encoding
		self.GET = FormParams()
		self.POST = FormParams()
		self.files = FormParams()

		if self.method == "POST":
			self._parse_post()
		elif self.method == "GET":
			self._parse_get()

		self.any = Any(self.GET, self.POST)


	def _parse_get(self):
		s = self.env.get("QUERY_STRING", "")
		self.GET = parse_query_string(s, self.encoding)

	def _parse_post(self):

		# error check and gather required env variables
		try:
			length = long(self.env["CONTENT_LENGTH"])
		except KeyError:
			raise FormInputClientError(
				"POST request without a CONTENT_LENGTH header.")
		except ValueError:
			raise FormInputClientError(
				"CONTENT_LENGTH header could not be converted to int.")
		try:
			content_type = self.env["CONTENT_TYPE"]
		except KeyError:
			raise FormInputClientError(
				"POST request without a CONTENT_TYPE header")


		# check the content-type and parse body accordingly
		if content_type == "application/x-www-form-urlencoded":
			body = self.env["wsgi.input"].read(length)
			self.POST = parse_query_string(body, self.encoding)
		elif content_type.startswith("multipart/form-data"):
			self.files, self.POST = parse_multipart(content_type,
					length, self.env["wsgi.input"], self.encoding)


	def get(self, name, default):
		""" Alias for any.get(name, default). """
		return self.any.get(name, default)

	def getfirst(self, name, default):
		""" Alias for any.getfirst(name, default). """
		return self.any.getfirst(name, default)

	def __call__(self, name, default=None):
		""" Alias for getfirst(name, default). """
		return self.getfirst(name, default)


class UrlManager(object):
	""" Simplifies url management/recreation.

	Examples
	========
		>>> env = {
		... 	'wsgi.url_scheme': "http",
		... 	'SERVER_NAME': "example.com",
		... 	'SERVER_PORT': "80",
		... 	'SCRIPT_NAME': "/home/share",
		... 	'PATH_INFO': "/test.cgi"
		... }
		>>> u = UrlManager(env)
		>>> u.http_host
		'example.com'
		>>> u.path
		['home', 'share', 'test.cgi']
		>>> u.create()
		'http://example.com/home/share/test.cgi'

		>>> env["SERVER_PORT"] = "8000"
		>>> UrlManager(env).http_host
		'example.com:8000'

		>>> env["HTTP_HOST"] = "www.example.com:90"
		>>> u = UrlManager(env)
		>>> u.http_host
		'www.example.com:90'
		>>> del u.path[-1]
		>>> u.create()
		'http://www.example.com:90/home/share'

	@ivar scheme: URL scheme like http, https or ftp.
			Defaults to the value in env["wsgi.url_scheme"] or
			an empty string if not in env.
	@ivar http_host: The host name and port like "example.com:3000".
			Defaults to env["HTTP_HOST"]. If HTTP_HOST is not in env,
			this is created from env["SERVER_NAME"] and env["SERVER_PORT"].
	@ivar path: A list where each entry is a part of the full path
			on the server. If we are at
			"http://example.com/my/test/app?test=20", path will be
			["my", "test", "app"].
	@ivar query_string: The part of the URL after ?. Defaults to
			a empty string.
	"""
	def __init__(self, env):
		"""
		@param env: A WSGI environ dict.
		"""
		self.scheme = env.get("wsgi.url_scheme", "")
		self.query_string = ""
		self.http_host = env.get("HTTP_HOST", "")
		if not self.http_host:
			self.http_host = env.get("SERVER_NAME", "")
			port = env.get("SERVER_PORT", "")
			if self.scheme == "http":
				if not port == "80":
					self.http_host += ":" + port
			if self.scheme == "https":
				if not port == "443":
					self.http_host += ":" + port
		self.path = env.get("SCRIPT_NAME", "").split("/")
		self.path.append(env.get("PATH_INFO", "/")[1:])
		if len(self.path) > 0 and self.path[0] == "":
			del self.path[0]

	def create(self):
		""" Generate/recreate the url. """
		url = self.scheme + "://" + self.http_host + "/" + "/".join(self.path)
		if self.query_string:
			url += "?" + self.query_string
		return url

	def __str__(self):
		""" Alias for L{create}. """
		return self.gen()


def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
