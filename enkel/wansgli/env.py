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

""" Tools to simplify working with WSGI environ dicts. """


from urlparse import urlparse
from re import compile, findall, VERBOSE
from urllib import quote


PARENT = 1
GRANDPARENT = 2

def parse_value(value):
	""" Parsers common environ value.

	Environ dicts usually contains a lot of values with
	this syntax:

	key=value; key2=value ...


	Example
	=======
		>>> x = "a=10; b=aXX3"
		>>> parse_value(x)
		{'a': '10', 'b': 'aXX3'}

		A more realistic example

		>>> env = dict(HTTP_COOKIE="sid=ax445; name=John")
		>>> parse_value(env["HTTP_COOKIE"])
		{'name': 'John', 'sid': 'ax445'}

	@see: L{parse_value_odd} for a slightly different value parser.
	@return: key-value-pair dict
	"""
	d = {}
	for k, v in findall("(\w+)=([^;]+)", value):
		d[k] = v
	return d


def parse_value_odd(value):
	""" Parses common environ value.

	Environ dicts usually contains a lot of values with
	this syntax:

	some-value; key=value; key2=value ...


	Example
	=======
		>>> x = "this is a test; a=10; b=aXX3"
		>>> parse_value_odd(x)
		('this is a test', {'a': '10', 'b': 'aXX3'})

	@return: (some-value, key-value-pair dict)
	"""
	a, b = value.split(";", 1)
	return a, parse_value(b)


def create_url(env, url_scheme=None, server_name=None,
		server_port=None, script_name=None, path_info=None,
		query_string="", http_host=None):
	""" Creates a url using L{reconstruct_url}, but if a parameter
	is not None, it overrides the one in env.
	
	Parameters means the same as their upper-case versions do
	in PEP 333. url_scheme is called wsgi.url_scheme in PEP 333.

	"script_name" can also be an integer or a list. If it is an
	integer, script_name is the number of levels to strip from
	the SCRIPT_NAME stored in env. 1 one will yield the parent
	folder and 2 two will yield the grandparent folder..
	You can use L{PARENT} and L{GRANDPARENT} instead of numbers
	to make your code more readable.

	If "script_name" is a list, the list will be joined by "/"
	to create SCRIPT_NAME.

	Example
	=======
		>>> env = {}
		>>> env["wsgi.url_scheme"] = "http"
		>>> env["SERVER_NAME"] = "example.com"
		>>> env["SERVER_PORT"] = "80"
		>>> env["SCRIPT_NAME"] = "/a/b"
		>>> env["PATH_INFO"] = "/test.cgi"
		>>> env["QUERY_STRING"] = "uid=xAcc"

		>>> create_url(env)
		'http://example.com/a/b/test.cgi'
		>>> create_url(env, path_info="/test2.cgi")
		'http://example.com/a/b/test2.cgi'

		>>> create_url(env, script_name=PARENT)
		'http://example.com/a/test.cgi'
		>>> create_url(env, script_name=["home", "peter"])
		'http://example.com/home/peter/test.cgi'

	@return: A URL as a str.
	"""
	if url_scheme == None:
		url_scheme = env.get("wsgi.url_scheme")
	if server_name == None:
		server_name = env.get("SERVER_NAME")
	if server_port == None:
		server_port = env.get("SERVER_PORT")
	if path_info == None:
		path_info = env.get("PATH_INFO")
	if query_string == None:
		query_string = env.get("QUERY_STRING")

	if script_name == None:
		script_name = env.get("SCRIPT_NAME")
	elif type(script_name) is int:
		script_name = "/".join(env.get("SCRIPT_NAME").split("/")[:-script_name])
	elif isinstance(script_name, (tuple, list)):
		script_name = "/" + "/".join(script_name)

	e = {
		"wsgi.url_scheme": url_scheme,
		"SERVER_NAME": server_name,
		"SERVER_PORT": server_port,
		"SCRIPT_NAME": script_name,
		"PATH_INFO": path_info,
		"QUERY_STRING": query_string
	}
	return reconstruct_url(e)


def reconstruct_url(env):
	""" Reconstruct a url from WSGI environ dict.

	Usage
	=====
		Minimal environ dict

		>>> env = {}
		>>> env["wsgi.url_scheme"] = "http"
		>>> env["SERVER_NAME"] = "mainpage.example.com"
		>>> env["SERVER_PORT"] = "80"
		>>> reconstruct_url(env)
		'http://mainpage.example.com'

		It uses HTTP_HOST if in the environ dict

		>>> env["HTTP_HOST"] = "example.com:3000"
		>>> reconstruct_url(env)
		'http://example.com:3000'

		Complete example

		>>> env["SCRIPT_NAME"] = "/a/b"
		>>> env["PATH_INFO"] = "/test.cgi"
		>>> env["QUERY_STRING"] = "uid=xAcc"
		>>> reconstruct_url(env)
		'http://example.com:3000/a/b/test.cgi?uid=xAcc'


	@param env: A WSGI environ dict.
	@return: The url.
	"""
	url = env['wsgi.url_scheme']+'://'

	if env.get('HTTP_HOST'):
		url += env['HTTP_HOST']
	else:
		url += env['SERVER_NAME']

		if env['wsgi.url_scheme'] == 'https':
			if env['SERVER_PORT'] != '443':
				url += ':' + env['SERVER_PORT']
		else:
			if env['SERVER_PORT'] != '80':
				url += ':' + env['SERVER_PORT']

	url += quote(env.get('SCRIPT_NAME',''))
	url += quote(env.get('PATH_INFO',''))
	if env.get('QUERY_STRING'):
		url += '?' + env['QUERY_STRING']
	return url


""" Used by L{urlpath_to_environ} """
PATHSPLIT_PATT = compile("""
		(.*)         # script name
		(/[^?/]*)    # path info
		(?:\?
			(.+)     # query string
		)?
	""", VERBOSE)

def urlpath_to_environ(env, urlpath):
	""" Parse the part of a url that comes after protocol and server
	info into a WSGI environ dict.

	Usage
	=====

		Complete path

		>>> env = dict()
		>>> urlpath_to_environ(env, "/my/cool/website.html?hello=world")
		>>> env.get("SCRIPT_NAME")
		'/my/cool'
		>>> env.get("PATH_INFO")
		'/website.html'
		>>> env.get("QUERY_STRING")
		'hello=world'

		Only a filename

		>>> env = dict()
		>>> urlpath_to_environ(env, "/website.html")
		>>> env.get("SCRIPT_NAME")
		''
		>>> env.get("PATH_INFO")
		'/website.html'
		>>> env.get("QUERY_STRING")
		''


	@param env: A WSGI environ dict. SCRIPT_NAME, PATH_INFO and
			QUERY_STRING entries are added/overwritten.
	@param urlpath: The "urlpath"
	"""
	env["SCRIPT_NAME"] = ""
	env["PATH_INFO"] = ""
	env["QUERY_STRING"] = ""
	if urlpath == "":
		return
	p = PATHSPLIT_PATT.match(urlpath).groups()
	if p[0]:
		env["SCRIPT_NAME"] = p[0]
	if p[1]:
		env["PATH_INFO"] = p[1]
	if p[2]:
		env["QUERY_STRING"] = p[2]


def url_to_environ(env, url):
	""" Parse a url into a WSGI environ dict.
	
	Usage
	=====
		>>> def print_sorted(env):
		... 	" print env sorted by key "
		... 	x = env.keys()
		... 	x.sort()
		... 	for key in x:
		... 		print "%-16s: '%s'" % (key, env[key])

		Complete url

		>>> env = dict()
		>>> url = "https://secure.example.com:91/a/b/c.cgi?name=john&x=10"
		>>> url_to_environ(env, url)
		>>> print_sorted(env)
		PATH_INFO       : '/c.cgi'
		QUERY_STRING    : 'name=john&x=10'
		SCRIPT_NAME     : '/a/b'
		SERVER_NAME     : 'secure.example.com'
		SERVER_PORT     : '91'
		wsgi.url_scheme : 'https'

		Url missing som parts

		>>> env = dict()
		>>> url = "https://secure.example.com/c.cgi"
		>>> url_to_environ(env, url)
		>>> print_sorted(env)
		PATH_INFO       : '/c.cgi'
		QUERY_STRING    : ''
		SCRIPT_NAME     : ''
		SERVER_NAME     : 'secure.example.com'
		SERVER_PORT     : '443'
		wsgi.url_scheme : 'https'


	@param env: A WSGI environ dict. wsgi.url_scheme, SERVER_NAME,
			SERVER_PORT, SCRIPT_NAME, PATH_INFO, QUERY_STRING
			entries are added/overwritten.
	@param url: A url.
	"""
	u = urlparse(url)

	# determine SERVER_NAME and PORT
	x = u[1].split(":", 1)
	env["SERVER_NAME"] = x[0]
	if len(x) > 1:
		port = x[1]
	elif u[0] == "https":
		port = "443"
	else:
		port = "80"
	env["SERVER_PORT"] = port

	# determine SCRIPT_NAME and PATH_INFO
	urlpath_to_environ(env, u[2])

	# query and scheme
	env["wsgi.url_scheme"] = u[0]
	env["QUERY_STRING"] = u[4]




def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from testhelpers import run_suite
	run_suite(suite())
