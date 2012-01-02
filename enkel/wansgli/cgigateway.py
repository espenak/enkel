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

""" WSGI cgi gateway. """

from os import environ
import sys

from apprunner import Response, run_app


def cgi_app_runner(app):
	""" Runs "app" in a CGI environment.

	CGI example script
	==================
		>>> import cgitb; cgitb.enable()
		>>> import sys

		>>> from enkel.wansgli.cgigateway import cgi_app_runner
		>>> from enkel.wansgli.demo_apps import simple_app

		>>> cgi_app_runner(simple_app)

	Put the above in a executable python script, and run it using
	a cgi server.

	@note: This code is almost a copy of the CGI gateway example in
			PEP 333. It will be replaced by a more powerfull class
			that supports logging ++ in the future.
	@param app: A WSGI app.
	"""
	env = dict(environ.items())
	env['wsgi.input'] = sys.stdin
	env['wsgi.errors'] = sys.stderr
	env['wsgi.version'] = (1,0)
	env['wsgi.multithread'] = False
	env['wsgi.multiprocess'] = True
	env['wsgi.run_once'] = True

	if env.get('HTTPS','off') in ('on','1'):
		env['wsgi.url_scheme'] = 'https'
	else:
		env['wsgi.url_scheme'] = 'http'

	req = Response(sys.stdout, env)
	run_app(app, req)
