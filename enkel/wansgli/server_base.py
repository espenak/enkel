"""
@var CGI_ENV_NAMES: A set containing the CGI variables which
	wansgli servers try to provide to apps.
"""


CGI_ENV_NAMES = set((
	"REQUEST_METHOD", "SCRIPT_NAME", "PATH_INFO", "QUERY_STRING",
	"CONTENT_TYPE", "CONTENT_LENGTH", "SERVER_PROTOCOL", "SERVER_NAME",
	"SERVER_PORT", "REMOTE_ADDR", "SERVER_SOFTWARE"
))


def check_required_headers(env):
	""" Check that all PEP 333 required environ variables
	are in 'env'.
	@raise ValueError: If the check fails.
	"""
	for name in ("REQUEST_METHOD", "SERVER_NAME",
			"SERVER_PORT", "SERVER_PROTOCOL"):
		if not name in env:
			raise ValueError(
				"Client did not send required header: %s" % name)


class LoggerAsErrorFile(object):
	""" Wraps a logger.Logger object in a interface compatible with
	the wsgi.errors object. """
	def __init__(self, log):
		"""
		@param log: A logger.Logger object.
		"""
		self.log = log
	def write(self, data):
		self.log.error(data)
	def writelines(self, seq):
		self.write("".join(seq))
	def flush(self):
		pass


class WsgiServerMixIn(object):
	""" A mixin class shared by all wansgli WSGI servers.
	Provides a common configuration api.

	@cvar RUN_ONCE: Should evaluate true if the server or gateway expects
		(but does not guarantee!) that the application will only be
		invoked this one time during the life of its containing process.
		Normally, this will only be true for a gateway based on CGI (or
		something similar).
	@cvar MULTIPROCESS: This value should evaluate true if an equivalent
		application object may be simultaneously invoked by another
		process, and should evaluate false otherwise.
	@cvar MULTITHREAD: 	this value should evaluate true if the application
		object may be simultaneously invoked by another thread in the
		same process, and should evaluate false otherwise.
	@cvar REQUEST_HANDLER: The request-handler used to handle requests.

	@ivar server_info: A short information string sent to clients
		using the "SERVER" header. Note that this can be
		overridden by the app.
	@ivar debug: Run in application-debugging mode.
		See L{apprunner.Response.__init__} for more information.
	@ivar log: The server log. A logging.Logger object.
	@ivar applog: A file-like object used as the "wsgi.errors" object.
		Only data sent specifically to "wsgi.errors" will end
		up here, uncaught exceptions end up in L{log}. If you
		want to use a logger.Logger object, wrap it in a
		L{LoggerAsErrorFile} object.
	@ivar app: The WSGI app to run. Read only.
	"""
	RUN_ONCE = False
	MULTIPROCESS = False
	MULTITHREAD = False

	server_info = "unknown" # for security
	debug = False


	def add_common_wsgienv(self, env):
		env.update({
			"wsgi.url_scheme": self.url_scheme,
			"wsgi.errors": self.applog,
			"wsgi.version": (1, 0),
			"wsgi.multithread": self.MULTITHREAD,
			"wsgi.multiprocess": self.MULTIPROCESS,
			"wsgi.run_once": self.RUN_ONCE
		})
