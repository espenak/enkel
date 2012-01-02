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

from re import compile
from os.path import join, isfile, isdir, islink
from os import listdir
from mimetypes import guess_type
from cStringIO import StringIO
from xml.sax.saxutils import quoteattr


class _FileIter(object):
	def __init__(self, path, buffersize):
		self.path = path
		self.buffersize = buffersize

	def __iter__(self):
		self.f = open(self.path, "rb")
		return self

	def next(self):
		while True:
			block = self.f.read(self.buffersize)
			if not block:
				raise StopIteration
			return block

	def close(self):
		if hasattr(self, "f"):
			self.f.close()


class StaticFiles(object):
	""" A WSGI static file/folder serving application.

	@cvar DEFAULT_CONTENT_TYPE: The default content-type used when
			content-type cannot be guessed.
	"""
	DEFAULT_CONTENT_TYPE = "application/octet-stream"
	def __init__(self, root_folder, prefix="",
				pattern=".*", buffersize=2048, follow_symlinks=False):
		"""
		Usage
		=====
			>>> app = StaticFiles("/my/shared/folder")

			And run "app" on a wsgi gateway.


		@param root_folder: the folder from where to serve files.
		@param pattern: A regular expression. Only files matching it
				will be shown.
		@param buffersize: The buffersize used when reading files.
		@param follow_symlinks: Follow symlinks?
		"""
		self.patt = compile(pattern)
		self.root_folder = root_folder
		self.buffersize = buffersize
		self.prefixlen = len(prefix)
		self.follow_symlinks = follow_symlinks


	def handle_notfound(self, env, start_response, path):
		""" Invoked by __call__ when a file that does not exist is requested.
		@param env: The WSGI environ dict sent to __call__.
		@param start_response: The start_response callable sent to __call__.
		@param path: The requested path without prefix.
		"""
		start_response("404 not found", [("content-type", "text/plain")])
		return ["%s does not exist" % path]

	def list_directory(self, env, start_response, path):
		""" Invoked by __call__ when a directory is requested. """
		if path.endswith("/"):
			path = path[:-1]
		folder = join(self.root_folder, path)
		buf = StringIO()
		print >> buf, "<html><body>"
		print >> buf, "<h1>%s%s</h1>" % (env["SCRIPT_NAME"],
				env["PATH_INFO"])
		print >> buf, "<ul>"
		for fn in listdir(folder):
			style = ""
			real_path = join(folder, fn)
			url_path = "%s/%s" % (path, fn)

			if islink(real_path) and not self.follow_symlinks:
				continue
			if not self.patt.match(url_path):
				continue

			if isdir(real_path):
				style = " style='font-weight: bold;'"
				fn += "/"
			elif not isfile(real_path):
				continue

			print >> buf, "\t<li%s><a href='%s'>%s</a></li>" % (
					style, fn, fn)

		print >> buf, "</ul>"
		print >> buf, "</body></html>"

		start_response("200 OK", [("content-type", "text/html")])
		return [buf.getvalue()]


	def __call__(self, env, start_response):
		path = env["SCRIPT_NAME"] + env["PATH_INFO"]
		path = path[self.prefixlen:]
		if path.startswith("/"):
			path = path[1:]
		real_path = join(self.root_folder, path)

		if islink(real_path) and not self.follow_symlinks:
			return self.handle_notfound(env, start_response, path)

		if not self.patt.match(path):
			return self.handle_notfound(env, start_response, path)

		if isdir(real_path):
			return self.list_directory(env, start_response, path)
		elif isfile(real_path):
			content_type = guess_type(real_path)[0] \
					or self.DEFAULT_CONTENT_TYPE
			start_response("200 OK", [("content-type", content_type)])
			return _FileIter(real_path, self.buffersize)

		return self.handle_notfound(env, start_response, path)
