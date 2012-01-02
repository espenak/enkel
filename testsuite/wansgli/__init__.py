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

from enkel.wansgli.testhelpers import unit_mod_suite, run_suite
from enkel.wansgli import apptester as dt_apptester, env as dt_env,\
		utils as dt_utils, response as dt_response, \
		formparse as dt_formparse, apputils as dt_apputils

import apprunner, formparse, scgi, http


def suite():
	return unit_mod_suite(apprunner, formparse, scgi, http,
			dt_apptester, dt_env, dt_utils, dt_formparse, dt_response,
			dt_apputils)

if __name__ == "__main__":
	run_suite(suite())
