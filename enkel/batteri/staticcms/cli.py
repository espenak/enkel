#!/usr/bin/env python
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


""" Command-line interface to staticcms. """

from optparse import OptionParser
from os.path import exists, join
from os import listdir
from sys import exit
from lxml.etree import LxmlError, parse
import logging

from create import create, parse_config
from validate_post import validate_post


def cli():
	p = OptionParser(
		usage = "%prog [options]",
		description = "'--validate' and/or '--create' options must be supplied. "\
			"If both are supplied, '--validate' is executed first, and "
			"if it fails the program aborts.")
	p.add_option("--validate", dest="validate", action="store_true",
			help="Validate all the given posts. If not -p is given, " \
			"validate all posts.")
	p.add_option("--create", dest="create", action="store_true",
			help="Create the cms.")
	p.add_option("-p", "--post-id", dest="post_id",
			help="The id(filename) of a post. Only used by the " \
			"--create action.")
	p.add_option("-c", "--config-file", dest="config_file",
			help="Path to the config-file. Defaults to staticcms.cfg.",
			default="staticcms.cfg")
	p.add_option("-v", "--verbose", dest="verbose", action="store_true",
			help="Show some extra informative output.")
	p.add_option("-d", "--very-verbose", dest="vverbose", action="store_true",
			help="Show debugging information. For theme writers.")
	(opt, args) = p.parse_args()



	if not (opt.validate or opt.create):
		p.print_help()
		exit(1)


	if opt.verbose:
		logging.basicConfig(level=logging.INFO)
	elif opt.vverbose:
		logging.basicConfig(level=logging.DEBUG)


	try:
		posts_folder, theme_folder, process_command, sync_command = \
				parse_config(opt.config_file)
	except Exception, e:
		if exists(opt.config_file):
			raise
		else:
			raise SystemExit("Config-file '%s' does not exist." % opt.config_file)


	def validate(post_id):
		try:
			validate_post(parse(join(posts_folder, post_id)))
			print "validate '%s': OK" % post_id
		except LxmlError, e:
			print "validate '%s': ERROR" % post_id
			x = []
			for err in e.error_log:
				x.append("%s: %s: line %s: %s" % (
						err.level_name, err.filename, err.line, err.message))
			raise SystemExit("\n".join(x))

	if opt.validate:
		if opt.post_id:
			posts = [opt.post_id]
		else:
			posts = listdir(posts_folder)
		for post_id in posts:
			validate(post_id)

	if opt.create:
		try:
			create(posts_folder, theme_folder, process_command, sync_command)
		except:
			log = logging.getLogger("enkel.batteri.staticcms")
			log.exception("--create failed.")



if __name__ == "__main__":
	cli()
