#!/usr/bin/env python

import BaseHTTPServer
import CGIHTTPServer
from os import chdir
import sys


def run(server_class=BaseHTTPServer.HTTPServer,
		handler_class=CGIHTTPServer.CGIHTTPRequestHandler, port=5000):
	server_address = ('', port)
	#handler_class.cgi_directories = ['']
	httpd = server_class(server_address, handler_class)
	httpd.serve_forever()


def cli():
	if len(sys.argv) > 2:
		chdir(sys.argv[1])
		run(port=int(sys.argv[2]))
	else:
		raise SystemExit("""usage: %s <base directory> <port>

	CGI scripts must be in <base directory>/cgi-bin/.


	About
	=====
		A simple cgi server in pure python. It is here to enable
		testing of cgi applications withiut the need of advanced
		server setups. Note that you can also use this program
		to serve static files.
	""" % sys.argv[0])


if __name__ == "__main__":
	cli()
