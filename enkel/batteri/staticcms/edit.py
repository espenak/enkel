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

from os import listdir, remove
from os.path import join, isfile
from re import compile, DOTALL, VERBOSE
import codecs

from enkel.wansgli.apputils import FormInput
from enkel.batteri.admin.admin import AdminApp
from enkel.model.util import ModelData, forminput_to_manip
from enkel.model import data
from enkel.model.field import base, reg, xmlf
from enkel.xmlutils.writer import XmlWriter
from enkel.wansgli.apptester import encode_query
from enkel.exml.formgen import Form
from enkel.exml.info import XMLNS_MARKUP

from create import create, parse_config, StaticcmsError
from validate_post import validate_post_field


XMLNS_STATICBLOG = "http://enkel.wsgi.net/xml/staticcms"
ENCODING = "utf-8"
N_ = lambda string: string


class ScmsIdString(reg.IdString):
	""" The field used for the "id" of posts by L{StaticCmsEdit}. """
	PATT = compile("^[a-z0-9_-]+$")
	ERRMSG = N_("can only contain a-z, 0-9, '_' and '-'")


class StaticCmsEdit(AdminApp):
	ACTIONS = dict(
		browse = N_("Browse"),
		create = N_("Create"),
		edit = N_("Edit"),
		save = N_("Save"),
		delete = N_("Delete"),
		rebuild = N_("Rebuild")
	)
	INDEX = ["browse", "create", "rebuild"]


	# the model used to create the input form for "post" editing.
	MODEL = dict(
		id = ScmsIdString(required=True),
		heading = base.String(45),
		summary = base.String(500),
		tags = base.String(500, required=False),
		post = xmlf.XmlField(offset=5, validate=validate_post_field,
			format = \
				"""<post xmlns="%(XMLNS_STATICBLOG)s">
					<summary/>
					<section xmlns="%(XMLNS_MARKUP)s"
							xmlns:s="%(XMLNS_STATICBLOG)s">
					<h>heading</h>
					%%s
					</section>
				</post>""" % globals()
		)
	)

	# metadata for the MODEL.
	META = {
		"id": {
			"shorthelp":
				N_("A unique identifier for the cms entry containing "\
				"only a-z, 0-9, '-' and '_'.")},
		"tags": {
			"shorthelp":
				N_("A list of tagnames separated with comma. "\
				"Like: 'Info, News'.")},
	}


	# pattern used to parse the "post" xml files into the MODEL.
	POST_PARSE_PATT = compile(
	""".*?
	<post.*?>
	.*?
		<summary>(?P<summary>.*?)</summary>
		(?P<tags>.*?)
		<section.*?>
			.*?
			<h>(?P<heading>.*?)</h>
			(?P<post>.*)
		</section>
	.*?
	</post>""", DOTALL|VERBOSE)

	# pattern used to split the "tags" output from POST_PARSE_PATT
	# into the "tags" list for the MODEL.
	TAGS_PARSE_PATT = compile("<tag>(.*?)</tag>", DOTALL)

	# pattern used to replace all "newlines" with \n.
	UNIVERSAL_NEWLINE_PATT = compile(r"(\r\n|\r)")

	def __init__(self, env, w, id, action, label,
				configfile):
		"""
		@param configfile: Path to the configfile for the cms.
		"""
		self.posts_folder, self.theme_folder, self.process_command, \
			self.sync_command = parse_config(configfile)
		super(StaticCmsEdit, self).__init__(
				env, w, id, action, label)


	def add_browse_actions(self, params):
		self.w.start_element("cell")
		self.w.start_element("strong",
				href="edit?" + encode_query(params))
		self.w.text_node(N_("edit"))
		self.w.end_element(2)

		self.w.start_element("cell")
		self.w.start_element("a",
				href="delete?" + encode_query(params))
		self.w.text_node(N_("delete"))
		self.w.end_element(2)


	def browse(self):
		self.w.start_element("p")
		self.w.start_element("table")

		for id in listdir(self.posts_folder):
			self.w.start_element("row")
			self.w.start_element("cell")
			self.w.text_node(id)
			self.w.end_element() # </entry>
			params = [("id", id)]
			self.add_browse_actions(params)
			self.w.end_element() # </row>

		self.w.end_element() # </table>


	def preform_edit_manip(self, manip):
		pass

	def _create_edit_form(self, manip, validate=False):
		self.preform_edit_manip(manip)
		form = Form("save", "Save", method="post")
		form["e_"] = ModelData(manip)
		form["e_"].meta = self.META
		if validate:
			form["e_"].validate()
		self.w.raw_node(form.create())

	def create(self):
		manip = data.Manip(self.MODEL)
		self._create_edit_form(manip)

	def edit(self):
		""" Open the post and parse it into a Manip using
		L{POST_PARSE_PATT} and L{TAGS_PARSE_PATT}. Then create
		a form from the manip using exml formgen. """

		id = FormInput(self.env).GET.getfirst("id")
		if not id:
			raise Exception("no id")
		path = join(self.posts_folder, id)
		post = codecs.open(path, "rb", ENCODING).read()

		r = self.POST_PARSE_PATT.match(post)
		tags = [m.group(1).strip() \
				for m in self.TAGS_PARSE_PATT.finditer(r.group("tags"))]

		manip = data.Manip(self.MODEL)
		manip.id = id
		manip.summary = r.group("summary").strip()
		manip.heading = r.group("heading").strip()
		manip.post = r.group("post").strip()
		manip.tags = ", ".join(tags)
		self._create_edit_form(manip)


	def save(self):
		manip = forminput_to_manip(self.MODEL, FormInput(self.env), "e_")
		try:
			manip.validate()
		except base.FieldValidationError:
			self._create_edit_form(manip, validate=True)
		else:
			p = XmlWriter(pretty=True)
			p.pi("xml", version="1.0", encoding=ENCODING)
			p.start_element("post", xmlns=XMLNS_STATICBLOG)

			p.start_element("summary")
			p.text_node(manip.summary)
			p.end_element()

			for tag in manip.tags.split(","):
				p.start_element("tag")
				p.text_node(tag.strip())
				p.end_element()

			p.start_element("section", xmlns=XMLNS_MARKUP,
					attrdict={"xmlns:s": XMLNS_STATICBLOG})
			p.start_element("h")
			p.text_node(manip.heading)
			p.end_element()
			p.raw_node(manip.post)
			p.end_element()

			p.end_element() # </post>

			path = join(self.posts_folder, manip.id)

			post = self.UNIVERSAL_NEWLINE_PATT.sub(r"\n", p.create())
			codecs.open(path, "wb", ENCODING).write(post)

			self.w.start_element("p")
			self.w.text_node(N_("Save successful"))
			self.w.end_element()


	def delete(self):
		id = FormInput(self.env).GET.getfirst("id")
		if not id:
			raise Exception("no id")
		path = join(self.posts_folder, id)
		remove(path)
		self.w.start_element("p")
		self.w.text_node(N_("Delete successful"))
		self.w.end_element()


	def rebuild(self):
		self.w.start_element("p")
		try:
			create(self.posts_folder, self.theme_folder,
					self.process_command, self.sync_command)
		except StaticcmsError, e:
			self.w.text_node(str(e))
		else:
			self.w.text_node(N_("Rebuild successful"))
		self.w.end_element()
