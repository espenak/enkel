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

from os import fork, setsid, chdir, dup2, getpid, umask, kill, remove
from os.path import join, exists, abspath
from stat import S_IWGRP, S_IWOTH, S_IROTH, S_IRGRP
from time import sleep
import logging, sys, signal



class Daemonize(object):
	""" Simplifies forking off a daemon process.
	
	Example
	=======
		>>> from time import sleep
		>>> import logging

		Create the daemon process:

		>>> class X(Daemonize):
		... 	def run(self, pid):
		... 		while 1:
		... 			print "In daemon-process with pid:", pid
		... 			sleep(0.1)
		... 	def finish(self):
		... 		print "Goodbye"


		Run the daemon process:

		>>> logging.basicConfig(level=logging.DEBUG)
		>>> p = X("/tmp/myprocess.pid")
		>>> p.start()

		Stop it after 4 seconds:

		>>> sleep(4)
		>>> p.stop()
	"""

	LOG = logging.getLogger("enkel.daemonize")
	KILL_COUNT = 10
	KILL_WAIT = 0.3

	def __init__(self, pidfile,
				workdir = "/",
				umask = S_IWGRP|S_IWOTH|S_IROTH|S_IRGRP,
				new_stdin = "/dev/null",
				new_stdout = "/dev/null",
				new_stderr = "/dev/null",
				okmsg = "Daemon-process with pid '%s' started."):
		self.pidfile = abspath(pidfile)
		self.workdir = workdir
		self.umask = umask
		self.new_stdin = new_stdin
		self.new_stdout = new_stdout
		self.new_stderr = new_stderr
		self.okmsg = okmsg


	def register_signal_handlers(self):
		""" Register signal handlers.
		Defaults to running L{finish}() on SIGTERM, and SIGINT.
		"""
		signal.signal(signal.SIGTERM, self._finish)
		signal.signal(signal.SIGINT, self._finish)


	def start(self):
		if exists(self.pidfile):
			raise OSError("pidfile %s is in use." % self.pidfile)

		try:
			pid = fork()
		except OSError, e:
			self.LOG.error("Failed to fork (first fork): %s" % e)
			sys.exit(1)
		if pid != 0:
			sys.exit(0) # exit first parent


		# start a new session
		chdir(self.workdir)
		setsid()
		umask(self.umask)

		try:
			pid = fork()
		except OSError, e:
			self.LOG.error("Failed to fork (second fork): %s" % e)
			sys.exit(2)
		if pid != 0:
			sys.exit(0) # exit second parent


		# now we are fully forked (independent of the parent process/shell)
		pid = getpid()
		try:
			f = open(self.pidfile, "wb")
			f.write(str(pid))
			f.flush()
			f.close()
		except IOError, e:
			self.LOG.error("Failed to create pid-file '%s': %s" % (
					self.pidfile, e))
			sys.exit(3)

		self.LOG.info(self.okmsg % pid)
		self.redirect_filestreams()
		self.register_signal_handlers()
		self.run(pid)
		self.remove_pidfile()


	def remove_pidfile(self):
		self.LOG.debug("removing pidfile.")
		remove(self.pidfile)


	def stop(self, nopidfile_fatal=True, signal=signal.SIGTERM):
		""" Stop the daemonized process.
		Reads the process id from pidfile (parameter to __init__) and
		send the given "signal" to the process. We try to kill the process
		L{KILL_COUNT} times and wait L{KILL_WAIT} times between each try.

		@param nopidfile_fatal: Should the absence of a pidfile cause
				sys.exit() to be called?
		@type nopidfile_fatal: bool
		@param signal: The signal to be sent to the process. You will probably
				only use signal.SIGTERM or signal.SIGKILL. Defaults to
				signal.SIGTERM.
		"""
		try:
			pid = open(self.pidfile).read()
		except IOError, e:
			if nopidfile_fatal:
				self.LOG.error("Failed to read pid-file '%s': %s" % (
						self.pidfile, e))
				sys.exit(4)
			else:
				self.LOG.info("Failed to read pid-file '%s': %s" % (
						self.pidfile, e))
				return
		else:
			try:
				pid = int(pid)
			except ValueError, e:
				self.LOG.error("Pid-file '%s' does not contain an integer." % pid)
				sys.exit(5)

		try:
			for count in xrange(self.KILL_COUNT):
				kill(pid, signal)
				sleep(self.KILL_WAIT)
		except OSError, e:
			if str(e).find("No such process"):
				if count == 0:
					self.LOG.info("Process with pid '%s' is not running." % pid)
				else:
					self.LOG.info("Process with pid '%s' stopped." % pid)
				self.remove_pidfile()
			else:
				raise


	def _redirect_filestream(self, name, newfile, flush=True):
		if flush:
			getattr(sys, name).flush()
		try:
			dup2(newfile.fileno(), getattr(sys, name).fileno())
		except AttributeError:
			setattr(sys, name, newfile)


	def redirect_filestreams(self):
		""" Redirect standard file streams. You should not need to override
		this. """
		#sys.stderr.flush()
		#sys.stdout.flush()
		if self.new_stdin:
			s = open(self.new_stdin, 'r')
			self._redirect_filestream("stdin", s, False)
		if self.new_stdout:
			s = open(self.new_stdout, 'a+')
			self._redirect_filestream("stdout", s)
		if self.new_stderr:
			s = open(self.new_stderr, 'a+', 0)
			self._redirect_filestream("stderr", s)


	def run(self, pid):
		""" Put the code you wish to daemonize here (override).
		@param pid: The process id.
		"""
		raise NotImplementedError()


	def _finish(self, signum, frame):
		self.finish()
		sys.exit(0)


	def finish(self):
		""" Called when the process is stopped.
		You can override which signals to connect this handler to
		in L{register_signal_handlers}. """
		pass



if __name__ == "__main__":
	from time import sleep

	class D(Daemonize):
		def run(self, pid):
			for x in xrange(5):
				print "%d) hello world from pid: %s" % (x, pid)
				sleep(2)
		def finish(self):
			print "Finished"

	logging.basicConfig(level=logging.DEBUG)
	p = D("/tmp/test.pid", new_stdout=None, new_stderr=None)

	action = sys.argv[1]
	if action == "start":
		p.start()
	elif action == "stop":
		p.stop()
	elif action == "restart":
		p.stop(False)
		p.start()
