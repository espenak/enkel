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

import re


class RESTroute(object):
	""" A RESTful routing middleware.

	How it works
	============
		RESTroute is responsible for forwarding requests to
		apps based on the REQUEST_METHOD and the "path" part of
		the url. With "path" we mean SCRIPT_NAME + PATH_INFO which
		are both WSGI environ variables (and defined in PEP 333).

		So lets say we have two wsgi applications named:
			- myapps.get_input
			- myapps.validate_input

		We could create a route like this::

			route = RESTroute()
			route.add("/input", GET=myapps.get_input)
			route.add("/validate", POST=myapps.validate_input)

		Now lets say our server is "https://example.com" and
		the "route" app is running there. A user visiting
		"https://example.com/input" would be routed/directed to
		myapp.get_input.

		Now let us assume this in an internationalized website and we
		use the URL to identify the preferred language. We could make
		the routing app place the preferred language in the WSGI
		environ variable "wsgiorg.routing_args" like this::

			route = RESTroute()
			route.add("/{w:lang}/input", GET=myapps.get_input)
			route.add("/{w:lang}/validate", POST=myapps.validate_input)

		The {w:lang} is the pattern language at work. "w" is called the
		"type-identifyer" and is defined L{here <types>}. "lang" is the
		name of the "wsgiorg.routing_args" keyword created when the
		url is matched. When a used visits "https:/example.com/en/input,
		they would get the english version of our app.. Or at least
		the application would be notified that english is the preferred
		language. What to do with this information is of course up
		to the application.


	The pattern
	===========
		The pattern sent as first argument to L{add} is already
		described above. But there are a litte bit more to it.

		A pattern can start with a "*". This means that it the
		pattern does not start matching at the first character
		in the "path".

		It can also end with ">". This means that the pattern does
		not match until the end of the "path". So both with
		the pattern "/home/test>", both "http://example.com/home/test"
		and "http://example.com/home/testing/my/car" would be matched.

		The two mechanisms described are mainly intended to enable
		nested routes (one route containing other routes). This
		is used in the example below.

		You can also specify optional parts of the pattern by
		enclosing them in []. Like this: "/{age}[/{gender}]"


	An example
	==========
		We use L{echo} to see what's going on behind the scenes.
		Anyone with a basic understanding of regular-expressions
		should be able to understand the regular expressions
		generated from patterns.

		>>> def app(env, start_response):
		... 	start_response("200 OK", [("content-type", "text/plain")])
		... 	return [str(env["wsgiorg.routing_args"])]
		>>> route = RESTroute()
		>>> route.echo = True
		>>> subroute = RESTroute()
		>>> subroute.echo = True

		>>> route.add("/{d:year}/{a:user}", GET=app)
		GET  /{d:year}/{a:user}  ^/(?P<year>\d+)/(?P<user>[a-zA-Z]+)$

		>>> subroute.add("*/{w:message}", GET=app)
		GET  */{w:message}  .*/(?P<message>\w+)$
		>>> route.add("/sub>", GET=subroute)
		GET  /sub>  ^/sub

		>>> route.add("/test[/{d:year}]", GET=app)
		GET  /test[/{d:year}]  ^/test(?:/(?P<year>\d+))?$



		Testing the result
		------------------
			>>> from enkel.wansgli.apptester import AppTester
			>>> t = AppTester(route, [], "http://example.com/2050/jack")
			>>> t.run_get().body
			"([], {'user': 'jack', 'year': '2050'})"

			>>> t = AppTester(route, [], "http://example.com/sub/hello")
			>>> t.run_get().body
			"([], {'message': 'hello'})"

			>>> t = AppTester(route, [], "http://example.com/test/100000")
			>>> t.run_get().body
			"([], {'year': '100000'})"

			>>> t = AppTester(route, [], "http://example.com/test")
			>>> t.run_get().body
			"([], {'year': None})"


	Adding your own types
	=====================
		An example of adding a type which matches our own narrow
		view of what is an animal.. We only look cow, tiger and dog:)

		>>> route = RESTroute()
		>>> route.types["animal"] = "(cow|tiger|dog)"
		>>> route.echo = True
		>>> route.add("/{animal:pet}", app)
		GET  /{animal:pet}  ^/(?P<pet>(cow|tiger|dog))$



	@ivar echo: If True, print some info about the patterns added
			with L{add}.
	@ivar types: A mapping of keywords to regular-expressions. Every
			node is a pair of (type-identifyer, regular-expression).
			Type-identifyers:
				- d: A whole number.
				- w: Word. 0-9, a-z, A-Z and '_'.
				- f: Filename. 0-9, a-z, A-Z, '_', '.' and '-'.
				- a: a-z and A-Z.
				- date: iso date. yyyy-mm-dd.
				- year: matches 4 digits.
				- x: Anything except /.
	"""
	type_expr = re.compile("\{([a-z]+):(\w+)\}")
	opt_expr = re.compile("\[([^\]]+)\]")
	def __init__(self):
		self.GET = []
		self.POST = []
		self.DELETE = []
		self.PUT = []
		self.echo = False
		self.types = dict(
			d = r"\d+",
			w = r"\w+",
			a = r"[a-zA-Z]+",
			f = r"[a-zA-Z0-9_.-]+",
			date = r"\d{4}-\d{2}-\d{2}",
			year = r"\d{4}",
			x = r"[^/]+"
		)


	def _opt_to_re(self, matchobj):
		return "(?:%s)?" % matchobj.group(1)

	def _type_to_re(self, matchobj):
		t, name = matchobj.groups()
		try:
			e = self.types[t]
		except KeyError:
			raise ValueError("unsupported type-identifyer: %s" % t)
		return "(?P<%s>%s)" % (name, e)

	def _patt_to_re(self, patt):
		""" Converts "patt" to regular expression. Used in L{add}.

		Some doctest
		============
			>>> r = RESTroute()

			>>> r._patt_to_re("/archives/{d:year}/{w:name}/{a:id}")
			'^/archives/(?P<year>\\\d+)/(?P<name>\\\w+)/(?P<id>[a-zA-Z]+)$'

			>>> r._patt_to_re("/archives/>")
			'^/archives/'

			>>> r._patt_to_re("*/{d:id}")
			'.*/(?P<id>\\\d+)$'

			>>> r._patt_to_re("/home[/a_{w:user}]")
			'^/home(?:/a_(?P<user>\\\w+))?$'
		"""
		e = self.opt_expr.sub(self._opt_to_re, patt)
		e = self.type_expr.sub(self._type_to_re, e)
		if patt.startswith("*"):
			e = "." + e
		else:
			e = "^" + e
		if patt.endswith(">"):
			e = e[:-1]
		else:
			e += "$"
		return e

	def add(self, patt, GET=None, POST=None, PUT=None, DELETE=None, env={}):
		r = self._patt_to_re(patt)
		l = locals()
		for method in "GET", "POST", "PUT", "DELETE":
			app = l[method]
			if app:
				getattr(self, method).append((patt, app, re.compile(r), env))
				if self.echo:
					print "%s  %s  %s" % (method, patt, r)

	def handle_notfound(self, env, start_response, path):
		""" Invoked by __call__ when a path with no application
		are requested.
		@param env: The WSGI environ dict sent to __call__.
		@param start_response: The start_response callable sent to __call__.
		@param path: The requested path without prefix.
		"""
		start_response("404 not found", [("content-type", "text/plain")])
		return ["%s does not exist" % path]

	def __call__(self, env, start_response):
		path = env["SCRIPT_NAME"] + env["PATH_INFO"]
		match = None
		for p, app, r, extra_env in getattr(self, env["REQUEST_METHOD"]):
			match = r.match(path)
			if match:
				kw = match.groupdict()
				env["wsgiorg.routing_args"] = ([], kw)
				env.update(extra_env)
				return app(env, start_response)
		return self.handle_notfound(env, start_response, path)



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
