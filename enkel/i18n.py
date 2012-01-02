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

""" Internationalization.

@var BUILTIN_LOCALEDIR: The folder containing the translations
		of the library.
@var BUILTIN_DOMAIN: The domain used for the library translations.
"""
from gettext import translation, NullTranslations
from os.path import split, join, dirname
from pkg_resources import resource_filename

from enkel.settings import encoding


BUILTIN_LOCALEDIR = resource_filename(__name__, "translations")
BUILTIN_DOMAIN = "default"
I18N_LANG_ENV = "enkel.i18n.lang"
I18N_ENV = "enkel.i18n"


class DomainBoxInterface(object):
	""" A DomainBox is a threadsafe interface to a gettext domain. """
	def __init__(self, domain, localedir,
				codeset = encoding,
				fallback = False):
		"""
		All parameters are forwarded to gettext.translations() when
		the gettext dictionary is loaded.
		"""
		self.domain = domain
		self.localedir = localedir
		self.codeset = codeset
		self.fallback = fallback
		self.trans = {}

	def add(self, langcode, *fallback_langcodes):
		""" Add a language to the box.
		@param langcode: The primary language.
		@param fallback_langcodes: Other languages that can be
				used when translations for "langcode" is not
				available.
		"""
		raise NotImplementedError()

	def get(self, langcode, fallback=NullTranslations()):
		""" Get the gettext dictionary for a language.
		@param langcode: A langcode added with L{add}.
		@param fallback: A gettext.NullTranslations compatible
				object to use as fallback if no dictionary for
				"langcode" is found.
		"""
		raise NotImplementedError()



class CacheDomainBox(DomainBoxInterface):
	""" A DomainBoxInterface implementation that loads all
	dictionaries into memory once. This gives very fast lookup,
	but uses alot of memory if you wish to support many
	languages.

	>>> d = CacheDomainBox(BUILTIN_DOMAIN, BUILTIN_LOCALEDIR)
	>>> d.add("nb")
	>>> d.get("nb").ugettext("Delete")
	u'Slett'
	>>> d.get("null").ugettext("Delete")
	u'Delete'
	"""
	def add(self, langcode, *fallback_langcodes):
		self.trans[langcode] = translation(
				self.domain, self.localedir,
				[langcode] + list(fallback_langcodes),
				fallback=self.fallback, codeset=self.codeset)

	def get(self, langcode, fallback=NullTranslations()):
		try:
			return self.trans[langcode]
		except KeyError:
			return fallback


class OnDemandDomainBox(DomainBoxInterface):
	""" A DomainBoxInterface implementation that loads
	dictionaries on demand, everytime L{get} is invoked.
	This only uses memory when the dictionary is loaded,
	and might be more effective than L{CacheDomainBox} when
	using lots of languages.

	>>> d = CacheDomainBox(BUILTIN_DOMAIN, BUILTIN_LOCALEDIR)
	>>> d.add("nb")
	>>> d.get("nb").ugettext("Delete")
	u'Slett'
	>>> d.get("null").ugettext("Delete")
	u'Delete'
	"""
	def add(self, langcode, *fallback_langcodes):
		self.trans[langcode] = fallback_langcodes

	def get(self, langcode, fallback=NullTranslations()):
		try:
			fallback_langcodes = self.trans[langcode]
		except KeyError:
			return fallback
		else:
			return translation(
				self.domain, self.localedir,
				[langcode] + list(fallback_langcodes),
				fallback=self.fallback, codeset=self.codeset)



def suite():
	import doctest
	return doctest.DocTestSuite()

if __name__ == "__main__":
	from enkel.wansgli.testhelpers import run_suite
	run_suite(suite())
