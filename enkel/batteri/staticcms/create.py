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

#!/usr/bin/env python


from subprocess import call
from os import listdir, system
from os.path import join
from shutil import copy, rmtree, copytree
from tempfile import mkdtemp
from ConfigParser import RawConfigParser
import logging

from enkel.xmlutils.writer import XmlWriter

from preprocess import preprocess


log = logging.getLogger("enkel.batteri.staticcms")

class StaticcmsError(Exception):
	""" Base class for all staticcms exceptions. """

class ProcessCmdFailed(StaticcmsError):
	""" Raised when the process_command in L{create} fails. """

class SyncCmdFailedError(StaticcmsError):
	""" Raised when the sync_command in L{create} fails. """



def prepare_env(tmpfolder, posts_folder, theme_folder):
	""" Prepare the temporary folder for XSLT processing of the theme.
	@param tmpfolder: The folder where the required environment
			will be created.
	@param posts_folder: The folder containing all the posts in the cms.
	@param theme_folder: The folder containing the theme.
	@return: (xsltfile, postlist_file)
	"""
	postlist_file = join(tmpfolder, "posts.xml")
	taglist_file = join(tmpfolder, "tags.xml")
	tmptheme_folder = join(tmpfolder, "theme")
	xsltfile = join(tmptheme_folder, "main.xsl")

	# Create the temporary environment required
	preprocess(postlist_file, taglist_file, posts_folder)
	log.debug("copying %s ==> %s" % (theme_folder, tmptheme_folder))
	copytree(theme_folder, tmptheme_folder)

	return xsltfile


def create(posts_folder, theme_folder, process_command, sync_command):
	r""" Process the XSLT files and create sync the changes to
	the public tree.

	@param posts_folder: The folder containing all the posts in the cms.
	@param theme_folder: The folder containing the theme.
	@param process_command: The command invoked to process the
			XSLT theme file. The XSLT file is "%(tmp)s/theme/main.xsl"
			and the XML file is "%(tmp)s/posts.xml".
	@param sync_command: The command invoked to sync the result to
			the public tree. The source-folder is "%(tmp)s/out".
	"""
	tmpfolder = mkdtemp(prefix="staticcms-")
	log.debug("created temp folder: %s" % tmpfolder)
	xsltfile = prepare_env(
			tmpfolder, posts_folder, theme_folder)

	sync_command = sync_command % dict(tmp=tmpfolder)
	process_command = process_command % dict(tmp=tmpfolder)
	try:
		retcode = system(process_command)
		log.info("%s returned %d" % (process_command, retcode))
		if retcode == 0:
			retcode = system(sync_command)
			log.info("%s returned %d" % (sync_command, retcode))
			if retcode != 0:
				raise SyncCmdFailedError(
					"Sync command failed with retcode %d!" % retcode)
		else:
			raise ProcessCmdFailed(
				"Process command failed with retcode %d!" % retcode)
	finally:
		rmtree(tmpfolder)



def parse_config(configfile):
	""" Parse a ConfigParser config-file.
	@return: (posts_folder, theme_folder, process_command, sync_command)
	"""
	cfg = RawConfigParser()
	cfg.read(configfile)

	r = []
	for key in "posts_folder", "theme_folder", "process_command", \
			"sync_command":
		r.append(cfg.get("main", key))
	return r
