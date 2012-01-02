#!/usr/bin/env python

import urllib
from sys import argv


def cli():
	if len(argv) < 2:
		raise SystemExit("""usage: %s <url>

	Purpose
	=======
		Test what your application/server actually shows to the
		client.
	""" % argv[0])

	f = urllib.urlopen(argv[1])
	print f.geturl()
	print
	print "-----------------[ header ] ---------------------"
	print f.info()
	print "-----------------[  body  ] ---------------------"
	print f.read()


if __name__ == "__main__":
	cli()
