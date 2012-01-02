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

from re import compile, VERBOSE
from os import listdir, stat
from os.path import isdir, join, exists
from shutil import rmtree
from tempfile import mkdtemp
import logging
from userdb_interface import UserDb, AuthorizationError, DomainError


log = logging.getLogger("enkel.batteri.auth.textfile_userdb")


class UserDb(object):
	USERSPATT = compile(r"""
		(?P<name>\w+)\s*:\s*
		(?P<domains>[a-zA-Z0-9_,]+)\s*:\s*
		(?P<passwd>\S+)
	""", VERBOSE)
	DOMAINSPATT = compile(r"[a-zA-Z0-9_]+")

	def __init__(self, dbfile, tmpfolder=None, max_attempts=10):
		if tmpfolder:
			if not isdir(tmpfolder):
				raise ValueError("'tmpfolder' must be an existing folder.")
			if not len(listdir(tmpfolder)) == 0:
				raise ValueError("'tmpfolder' must be empty.")
		else:
			tmpfolder = mkdtemp(prefix="enkel..textfile_userdb", suffix="-tmp")
		log.info("tmpfolder: %s" % tmpfolder)

		self.tmpfolder = tmpfolder
		self.dbfile = dbfile
		self.max_attempts = max_attempts
		self.users = {}

		for m in self.USERSPATT.finditer(open(dbfile, "rb").read()):
			u = m.groupdict()
			domains = self.DOMAINSPATT.findall(u["domains"])
			self.users[u["name"]] = (u["passwd"], domains)


	def close(self):
		""" Remove 'tmpfolder'. """
		log.info("removing %s" % self.tmpfolder)
		rmtree(self.tmpfolder)


	def authenticate(self, env, username, passwd, domain):
		user = self.users.get(username)
		if user:
			errfile = join(self.tmpfolder, username)
			attempts = 0
			if exists(errfile):
				s = stat(errfile)
				attempts = s.st_size
				if attempts >= self.max_attempts:
					raise AuthorizationError()

			stored_pwd, domains = user
			if not stored_pwd == passwd:
				attempts += 1
				log.info("failed login (%d) for user '%s' from host '%s'" % (
					attempts, username, env["REMOTE_ADDR"]))
				open(errfile, "ab").write("x")

				if (attempts) == self.max_attempts:
					log.info("%d failed attempts for user '%s'. Account locked." % (
						attempts, username))
				raise AuthorizationError()
			if not domain in domains:
				raise DomainError()
		else:
			raise AuthorizationError()
