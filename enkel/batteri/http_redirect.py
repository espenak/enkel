class HttpRedirect(object):
	def __init__(self, url):
		self.url = url
	
	def __call__(self, env, start_response):
		start_response("302 Found", [
			("content-type", "text/html"),
			("location", self.url)
			])
		yield """<html><body>
		Redirecting to <a href="%s">%s</a>.</body></html>
		""" % (self.url, self.url)


if __name__ == "__main__":
	from enkel.wansgli.http import Server
	Server(HttpRedirect("http://www.example.com")).serve_forever()
