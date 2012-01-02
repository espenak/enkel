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
from xml.sax import make_parser, parse
from xml.sax.handler import ContentHandler, feature_namespaces
from os import listdir
from os.path import join, abspath, getmtime
from time import gmtime, strftime
import logging

from enkel.xmlutils.writer import XmlWriter


log = logging.getLogger("enkel.batteri.staticcms")



TO_ID_PATT = compile(r"[^a-zA-Z0-9_-]")
def to_id(heading):
	heading = heading.replace(" ", "_")
	return TO_ID_PATT.sub("", heading).lower()


class PostHandler(ContentHandler):
	""" Sax handler used by L{preprocess} to parse a post file. """
	def __init__(self, post_id, tags):
		self.post_id = post_id
		self.tags = tags
		self.buf = []
		self.intag = False
		ContentHandler.__init__(self)

	def startElement(self, name, attrs):
		if name == "tag":
			self.buf = []
			self.intag = True

	def characters(self, contents):
		if self.intag:
			self.buf.append(contents)

	def endElement(self, name):
		if name == "tag":
			self.intag = False
			tag_name = "".join(self.buf).strip()
			if not tag_name == "":
				tag_id = to_id(tag_name)
				if tag_id in self.tags:
					self.tags[tag_id][1].append(self.post_id)
				else:
					self.tags[tag_id] = (tag_name, [self.post_id])



def preprocess(postlist_filename, taglist_filename, posts_folder):
	""" Create a xml-file containing listing all the posts in the cms
	and a file containing all the tags is the cms.

	The format of the file output-files are defined in
	relax-ng/posts.rng and relax-ng/tags.rng.

	@param postlist_filename: The file where the post info is written.
	@param taglist_filename: The file where the tag info is written.
	@param posts_folder: The folder containing all the post-files.
	"""
	tags = {}
	w = XmlWriter(pretty=True)

	w.start_element("posts")
	for post_id in listdir(posts_folder):
		path = join(posts_folder, post_id)
		w.empty_element("post",
			id = str(post_id),
			src = abspath(path),
			mtime = strftime("%Y-%m-%d %H:%M", gmtime(getmtime(path)))
		)

		parser = make_parser()
		parser.setContentHandler(PostHandler(post_id, tags))
		parser.parse(path)
	w.end_element()

	# write post list
	postslist = w.create().encode("utf-8")
	log.debug("%s: %s" % (postlist_filename, postslist))
	open(postlist_filename, "wb").write(postslist)

	# write tag list
	w = XmlWriter(pretty=True)
	w.start_element("tags")
	for tag_id in tags:
		tag_name, posts = tags[tag_id]
		w.start_element("tag", id=tag_id, name=tag_name)
		for post_id in posts:
			path = abspath(join(posts_folder, post_id))
			w.empty_element("post",
				id = post_id,
				src = path,
				mtime = strftime("%Y-%m-%d %H:%M", gmtime(getmtime(path)))
			)
		w.end_element()
	w.end_element()
	taglist = w.create().encode("utf-8")
	log.debug("%s: %s" % (taglist_filename, taglist))
	open(taglist_filename, "wb").write(taglist)
