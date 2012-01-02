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

""" A administration panel interface using exml. """


from re import compile

from enkel.error.http import Http404
from enkel.xmlutils.writer import XmlWriter
from enkel.exml.info import XMLNS_MARKUP
from enkel import settings

from settings import XMLNS_ADMIN


class AdminApp(object):
	r""" Superclass for admin applications (applications to
	be served through a L{Admin}).

	Example
	=======
		>>> class TextAdmin(AdminApp):
		... 	ACTIONS = dict(
		... 		edit = "Edit text",
		... 		create = "Create text",
		... 		browse = "Browse texts"
		... 	)
		...
		... 	# We do not add the 'edit' action as it will be
		... 	# accessed through the 'browse action'
		... 	INDEX = ["create, "edit"]
		...
		... 	def edit(self):
		... 		" Writes a browsing table to self.w. "
		...
		... 	def create(self):
		... 		" writes a form for editing a text to self.w. "
		...
		... 	def edit(self):
		... 		" same as create(), but with stored values already in the form. "


	@ivar env: The WSGI environment the L{Admin} serving
			this app was called with.
	@ivar w: A L{enkel.xmlutils.writer.XmlWriter} object.
			This is where the app must write its output.
	@ivar id: The id of the application. This is the id selected
			in L{Admin.add}.
	@ivar action: The requested action.
	@ivar label: The label of the application. This is the
			label selected in L{Admin.add}.

	@cvar ACTIONS: A dictionary with action as key and
			label as value. The action must be a function
			in this class. Action functions do not take any
			arguments.
	@cvar INDEX: A list of actions which should be selectable
			in the menu of the admin page.
	"""

	ACTIONS = {}
	INDEX = []

	def __init__(self, env, w, id, action, label):
		"""
		@raise enkel.error.http.Http404: If the action is
				not in L{ACTIONS}.

		@param env: See L{env} in the class documentation.
		@param w: See L{w} in the class documentation.
		@param id: See L{id} in the class documentation.
		@param action: See L{action} in the class documentation.
		@param label: See L{label} in the class documentation.
		"""
		self.env = env
		self.w = w
		self.id = id
		self.action = action
		self.label = label
		self.action = action

		if action in self.ACTIONS:
			self.w.start_element("h")
			self.w.text_node(self.get_heading(action))
			self.w.end_element()
			getattr(self, action)()
		else:
			raise Http404(long_message="unknown action: '%s'." % action)

	def get_heading(self, action):
		""" Get the heading for a action.
		You can override this in subclasses to provide a custom
		heading to your app.

		@param action: The requested action.
		@return: A heading for the action. Defaults to
				L{label}::L{ACTIONS}[action].
		"""
		return "%s::%s" % (self.label, self.ACTIONS[action])


def default_startpage(env, w):
	""" The default startpage function for L{Admin}.

	Parameters means the same as in L{AdminApp.__init__}
	"""
	w.start_element("p")
	w.text_node("Welcome to the Enkel administation panel.")
	w.end_element()


class Admin(object):
	""" A administration-panel interface using exml. """
	def __init__(self, stylesheet, encoding=settings.encoding,
				pretty=False, startpage=default_startpage):
		"""
		@param stylesheet: The URL to a XSLT document to associate
			with the output.
		@param encoding: The encoding to output in. Defaults
			to L{enkel.settings.encoding}.
		@param pretty: Forwarded to
			L{enkel.xmlutils.writer.XmlWriter.__init__}.
		@param startpage: A function which creates the startpage.
			Defaults to L{default_startpage}.
		"""
		self.apps = {}
		self.pretty = pretty
		self.applist = XmlWriter(pretty=pretty)
		self.applist.start_element("applist")
		self.encoding = encoding
		self.stylesheet = stylesheet
		self.startpage = startpage

	def add(self, id, app, label, *args, **kw):
		"""
		@type id: str
		@param id: A unique indentifier for the app within
				this Admin object.
		@param app: A L{AdminApp} instance.
		@type label: unicode.
		@param label: The label to show to the user when referencing
				the app.
		@param args: Arguments to the app.__init__.
		@param kw: Keyword arguments to the app.__init__.
		"""
		self.apps[id] = app, label, args, kw

		self.applist.start_element("app", id=id, label=label)
		for action in app.INDEX:
			self.applist.empty_element("action", id=action,
					label=app.ACTIONS[action])
		self.applist.end_element()


	def compile(self):
		""" Compile the route. Must be called once after
		all AdminApp's has been L{add}ed. """
		ids = "|".join(self.apps.keys())
		self.patt = compile(".*(?P<appid>(?:%s))/(?P<action>\w+)$" % ids)
		self.applist_xml = self.applist.create()
		del self.applist


	def __call__(self, env, start_response):
		"""
		env["enkel.reuse.admin.stylesheet"] must contain the
		URL to the XSLT stylesheet.
		"""

		path = env["SCRIPT_NAME"] + env["PATH_INFO"]
		appid = None
		if not path.endswith("start/"):
			match = self.patt.match(path)
			if match:
				appid, action = match.groups()
				app, label, args, kw = self.apps[appid]
			else:
				raise Http404()


		w = XmlWriter(pretty=self.pretty)
		w.pi("xml", version="1.0", encoding=self.encoding)
		w.pi("xml-stylesheet", type="text/xsl", href=self.stylesheet)
		w.start_element("admin", xmlns=XMLNS_ADMIN)
		w.raw_node(self.applist_xml)

		if appid:
			w.empty_element("selected", app=appid, action=action)
		w.start_element("section", xmlns=XMLNS_MARKUP)
		if appid:
			app(env, w, appid, action, label, *args, **kw)
		else:
			self.startpage(env, w)
		w.end_element()

		start_response("200 OK", [
			("content-type", "text/xml; charset=%s" % self.encoding)
		])
		yield w.create().encode(self.encoding)
