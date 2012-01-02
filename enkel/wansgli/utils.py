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

""" Functions used in one or more of the other modules that
might be useful in WSGI applications.

@var RFC1123_WEEKDAYS: rfc1123 compatible weekday names.
@var RFC1123_MONTHS: rfc1123 compatible month names.
@var BUF_SIZE: Buffer size used by L{read_until}
"""

from cStringIO import StringIO


BUF_SIZE = 512
RFC1123_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
RFC1123_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
		"Sep", "Oct", "Nov", "Dec")

def rfc1123_date(datetimeObj):
	""" Convert datetimeObj to the rfc 1123 format used by HTTP
	Date header field.

	For the result to be correct, the datetimeObj must be in
	GMT/UTC time.

	Does not use stftime to do locale dependent conversions.

	Example
	=======
		>>> from datetime import datetime
		>>> rfc1123_date(datetime(2006, 11, 12, 8, 12, 31))
		'Sun, 12 Nov 2006 08:12:31 GMT'
	"""
	format = "%s, %%d %s %%Y %%H:%%M:%%S GMT" % (
			RFC1123_WEEKDAYS[datetimeObj.weekday()],
			RFC1123_MONTHS[datetimeObj.month - 1])
	return datetimeObj.strftime(format)


def import_mod(modpath):
	""" Import a module by string.

	Example
	=======
		>>> m = import_mod("os.path")
		>>> hasattr(m, "abspath")
		True

	@param modpath: The module path as a string.
	@return: The requested module.
	"""
	mod = __import__(modpath)
	components = modpath.split(".")
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

def import_attr(attrpath):
	""" Import a attribute from a module.

	Example
	=======
		>>> from os import linesep
		>>> import_attr("os.linesep") == linesep
		True

	@param attrpath: The attribute-path as a string.
	@return: The requested module attribute.
	"""
	modpath, attrname = attrpath.rsplit(".", 1)
	mod = import_mod(modpath)
	return getattr(mod, attrname)



def read_until(istream, ostream, token, maxread=None,
		bufsize=BUF_SIZE, before=""):
	""" Find token in istream.

	Read from istream until token is found, "maxread" bytes are
	read or end-of-file. Everything before token is written to
	ostream. A token will usually be found in the middle of a
	buffer, so the function returns the rest of the buffer
	(except token).

	Examples (and tests)
	====================
		>>> from cStringIO import StringIO

		Simple test
		-----------
		>>> istream = StringIO("hello there 12345 world!!")
		>>> ostream = StringIO()
		>>> read_until(istream, ostream,
		... 	"12345", bufsize=10)
		(20, True, ' wo')
		>>> ostream.getvalue()
		'hello there '

		Bufsize 1 (should work)
		-----------------------
		>>> istream = StringIO("hello there 12345 world!!")
		>>> ostream = StringIO()
		>>> read_until(istream, ostream, "12345",
		... 	bufsize=1)
		(17, True, '')
		>>> ostream.getvalue()
		'hello there '

		Default bufsize
		---------------
		>>> istream = StringIO("hello there 12345 world!!")
		>>> ostream = StringIO()
		>>> read_until(istream, ostream, "12345")
		(25, True, ' world!!')
		>>> ostream.getvalue()
		'hello there '

		Maxread
		-------
		>>> istream = StringIO("hello there 12345 world!!")
		>>> ostream = StringIO()
		>>> read_until(istream, ostream, "12345",
		... 	maxread=3)
		(3, False, 'hel')
		>>> ostream.getvalue()
		''

		Overlap
		-------
		>>> istream = StringIO("hello there 12345 world!!")
		>>> ostream = StringIO()
		>>> read_until(istream, ostream, "12",
		... 	before="test nr 12..")
		(0, True, '..')
		>>> ostream.getvalue()
		'test nr '


	@param istream: A file-like object supporting read(size) open
			for reading.
	@param ostream: A file-like object supporting write(str) open
			for writing.
	@param token: The string to search for.
	@param maxread: The maximum number of bytes to read from
			buffer. If bool(maxread) == False, maxread is ignored.
	@param bufsize: The number of bytes to read from istream at a
			time. Defaults to L{BUF_SIZE} if bool(bufsize) == False.
	@param before: Include a string before the istream in the search.
			This is ment as a way to continue searching the same
			stream, and using the returned 'rest' as 'before' in
			the next search.

	@return: (bytes-read, token-found, rest), explained above
	@rtype: (int, bool, string)
	"""

	# bytes_read is the number of bytes read from istream
	if before:
		bytes_read = -len(before) # we cannot include before in bytes_read.
	else:
		bytes_read = 0

	before = StringIO(before)
	streams = (before, istream).__iter__()
	wstream = streams.next()

	# must use a overlap in case token is spread over more than
	# one buffer buffer
	olen = len(token) - 1  # overlap size
	overlap = ""
	
	while(True):
		if maxread:
			if bytes_read + bufsize > maxread:
				bufsize = maxread - bytes_read
			if bufsize == 0:
				return (bytes_read, False, overlap)

		# read from working buffer and search for token
		b = wstream.read(bufsize)
		bytes_read += len(b)
		buf = overlap + b
		i = buf.find(token)


		if i == -1:
			# token not found. write buf (except overlap) to
			# ostream.
			blen = len(buf)
			if blen > olen:
				l = olen
			else:
				l = blen
			overlap = buf[blen-l:]
			ostream.write(buf[:blen-l])

		else:
			# token found. return the rest of buf (except token)
			ostream.write(buf[:i])
			rest = buf[i+len(token):]
			return (bytes_read, True, rest)

		# goto next buffer if this buffer end is reached
		if len(b) < bufsize:
			try:
				wstream = streams.next()
			except StopIteration:
				return (bytes_read, False, 0)



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from testhelpers import run_suite
	run_suite(suite())

