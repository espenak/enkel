#!/usr/bin/env python


from urllib import urlencode, urlopen
from datetime import datetime
from sys import argv, exit

from enkel.wansgli.threadpool import ThreadPool


HELP = """usage: %(prog)s <url> <concurrecy> <count>

Send <count> requests to <url>. <concurrecy> connections
are attempted at the same time.

Note that the number of concurrent connections possible
depends on your underlying os, and the current system load.


Purpose
=======
	Test how well a web application performs on different
	server configurations.


Example
=======
	~$ %(prog)s http://localhost:8000 10 2000

	Send 2000 connections to locahost port 8000. Tries to
	process 10 request at the same time. On servers capable
	of handling more than one request at a time, this should
	be 8-10 times faster than:

		~$ %(prog)s http://localhost:8000 1 2000

	But if the response is fast, the speedup migth not be noticed.
"""


def fetch(num, url, verbose, args):
	f = urlopen(url, *args)
	body = f.read()
	if verbose:
		url = f.geturl()
		header = f.info()
		print "\n\n*%(url)s*\n%(header)s%(body)s" % vars()
		print "** got", num
	f.close()


def benchmark(concurrecy, count, verbose, url):
	args = []

	start = datetime.now()
	pool = ThreadPool(concurrecy)
	for num in range(count):
		if verbose:
			print "** sent", num
		pool.add_thread(fetch, num, url, verbose, args)
	pool.join()
	end = datetime.now()

	time_used = end - start
	return time_used


def cli():
	try:
		url = argv[1]
		concurrecy = int(argv[2])
		count = int(argv[3])
	except Exception, e:
		prog = argv[0]
		raise SystemExit(HELP % vars())

	t = benchmark(concurrecy, count, False, url)
	print "time used (hh:mm:ss..): %s" % t


if __name__ == "__main__":
	cli()
