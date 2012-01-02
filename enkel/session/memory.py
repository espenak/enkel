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

from datetime import datetime, timedelta

from backend import SessionBackend, NoSuchSessionError


class MemorySession(SessionBackend):
	""" Session management entirely in memory. """
	def __init__(self, timeout=timedelta(seconds=3600),
				delete_interval=timedelta(seconds=60*5)):
		"""
		@param timeout: The lifetime of a inactive session before it
				is deleted.
		@type timeout: datetime.timedelta
		@param delete_interval: Interval at which to delete old
				sessions.
		@type delete_interval: datetime.timedelta
		"""
		self.timeout = timeout
		self.delete_interval = delete_interval
		self.last_delete = datetime.now()
		self.sessions = dict()

	def save(self, sid, session):
		self._remove_old_on_interval()
		self.sessions[sid] = datetime.now(), session

	def load(self, sid):
		self._remove_old_on_interval()
		try:
			return self.sessions[sid][1]
		except KeyError:
			raise NoSuchSessionError("session '%s' does not exist." % sid)

	def _remove_old_on_interval(self):
		""" Remove old if last_delete is more than delete_interval ago. """
		m = datetime.now() - self.delete_interval
		if self.last_delete <= m:
			self._remove_old()

	def _remove_old(self):
		old = []
		min_time = datetime.now() - self.timeout
		for sid, session in self.sessions.iteritems():
			timestamp = session[0]
			if timestamp <= min_time:
				old.append(sid)
		for sid in old:
			del self.sessions[sid]
		self.last_delete = datetime.now()
