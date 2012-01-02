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


from sys import exc_info



class HttpHeaders(object):
	def __init__(self):
		self.headers = []

	def add_header(self, name, value):
		"""
		@param name: Name of the http header.
		@param value: Header value.
		"""
		self.headers.append((name, value))

	def add_headers(self, *headers):
		"""
		@param headers: List of (name, value) pairs. name and
				value are the same as in L{add_header}.
		"""
		self.headers.extend(headers)

	def __iter__(self):
		return self.headers.__iter__()


class ContentType(HttpHeaders):
	"""
	@cvar CONTENT_TYPE: A mime-type.
	@cvar CHARSET: See the 'charset' parameter to L{__init__}.
	"""
	CONTENT_TYPE = None
	CHARSET = None
	def __init__(self, filename=None, charset=None):
		"""
		@param filename: If given, the browser will present the
				file/document as a download with 'filename' as
				default file-name.
		@param charset: The character encoding used on the document.
				If not given, it defaults to L{CHARSET}. If both
				charset and L{CHARSET} are None, no charset is
				sent to the client.
		"""
		super(ContentType, self).__init__()
		charset = charset or self.CHARSET
		if charset:
			value = "%s; charset=%s" % (self.CONTENT_TYPE, charset)
		else:
			value = self.CONTENT_TYPE
		self.add_header("content-type", value)

		if filename:
			self.add_header("content-disposition",
					"attachment; filename=%s" % filename)

class CThtml(ContentType):
	CONTENT_TYPE = "text/html"
	CHARSET = "utf-8"
class CTxhtml(ContentType):
	"""
	WARNING
	=======
		Older browsers act strange using this content type.
		You might want to serve xhtml pages using L{CThtml}.
	"""
	CONTENT_TYPE = "application/xml+xhtml"
	CHARSET = "utf-8"
class CTxml(ContentType):
	CONTENT_TYPE = "text/xml"
	CHARSET = "utf-8"
class CTplain(ContentType):
	CONTENT_TYPE = "text/plain"
class CTcss(ContentType):
	CONTENT_TYPE = "text/css"


class CTpdf(ContentType):
	CONTENT_TYPE = "application/pdf"
class CTpostscript(ContentType):
	CONTENT_TYPE = "application/postscript"
class CTrtf(ContentType):
	CONTENT_TYPE = "application/rtf"
class CTjavascript(ContentType):
	CONTENT_TYPE = "application/javascript"
class CTshockwave_flash(ContentType):
	CONTENT_TYPE = "application/x-shockwave-flash"
class CToctet(ContentType):
	""" Arbitrary byte stream. This is thought of as the "default"
	media type used by several operating systems, often used to
	identify executable files, files of unknown type, or files that
	should be downloaded in protocols that do not provide a separate
	"content disposition" header. """
	CONTENT_TYPE = "application/octet-stream"


class CTmpeg_audio(ContentType):
	""" MP3 or other MPEG audio. """
	CONTENT_TYPE = "audio/mpeg"
class CTwma(ContentType):
	""" Windows Media Audio. """
	CONTENT_TYPE = "audio/x-ms-wma"
class CTwav(ContentType):
	""" WAV audio. """
	CONTENT_TYPE = "audio/x-wav"


class CTgif(ContentType):
	CONTENT_TYPE = "image/gif"
class CTpng(ContentType):
	CONTENT_TYPE = "image/png"
class CTjpeg(ContentType):
	CONTENT_TYPE = "image/jpeg"
class CTtiff(ContentType):
	CONTENT_TYPE = "image/tiff"
class CTsvg(ContentType):
	CONTENT_TYPE = "image/svg+xml"
	CHARSET = "utf-8"


class CTmpeg_video(ContentType):
	CONTENT_TYPE = "video/mpeg"
class CTquicktime(ContentType):
	CONTENT_TYPE = "video/quicktime"
class CTwmv(ContentType):
	CONTENT_TYPE = "video/x-ms-wmv"


class Response(HttpHeaders):
	r"""
	Examples
	========
		>>> from enkel.wansgli.apptester import AppTester

		As simple as it gets
		--------------------

		>>> def app1(env, start_response):
		... 	r = Response(start_response)
		... 	r.add_headers(*CThtml())
		... 	r.start()
		... 	yield "app1"

		>>> r = AppTester(app1).run_get()
		>>> r.body
		'app1'
		>>> r.headers["content-type"]
		'text/html; charset=utf-8'


		Serving a downloadable svg file
		-------------------------------

		>>> image = '''
		... <svg width="100%" height="100%" version="1.1"
		... 		xmlns="http://www.w3.org/2000/svg">
		... 	<circle cx="100" cy="50" r="100" stroke="black"
		... 			stroke-width="2" fill="red"/>
		... </svg>'''

		>>> def app2(env, start_response):
		... 	r = Response(start_response)
		... 	r.add_headers(*CTsvg("image.svg"))
		... 	r.start()
		... 	yield image

		>>> r = AppTester(app2).run_get()
		>>> r.headers["content-type"]
		'image/svg+xml; charset=utf-8'
		>>> r.headers["content-disposition"]
		'attachment; filename=image.svg'

		@ivar status: The http status code. Defaults to "200 0K".
	"""
	def __init__(self, start_response):
		self.start_response = start_response
		self.status = "200 OK"
		self.headers = []

	def start(self):
		""" Run start_response(self.status, self.headers). """
		self.start_response(self.status, self.headers)

	def error(self, status="500 Error"):
		""" Run start_response(status, self.headers, sys.exc_info()). """
		self.start_response(status, self.headers, exc_info())


def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
