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

""" Helpers for automatic testing.

Unit testing example
====================

	>>> import unittest


	>>> class MyTest(unittest.TestCase):
	... 	" a unit-test "
	... 	def test_the_obvious(self):
	... 		self.assert_(1+1 == 2)


	>>> def suite():
	... 	" The suite creation method "
	... 	return unit_case_suite(MyTest)

	>>> if __name__ == '__main__':
	... 	run_suite(suite())


Doctest testing example
=======================

	>>> def add(a, b):
	... 	\"\"\" a doctest'ed function.
	... 	>>> add(1, 2)
	... 	3
	... 	\"\"\"
	... 	return a + b


	>>> def suite():
	... 	" The suite creation method "
	... 	import doctest
	... 	return doctest.DocTestSuite()

	>>> if __name__ == "__main__":
	... 	run_suite(suite())
	"""

import unittest, sys, doctest
from cStringIO import StringIO


def unit_suite(*test_suites):
	""" Create a unit testsuite containing the given test_suites.
	@return: The new testsuite.
	@rtype: unittest.TestSuite
	"""
	suite = unittest.TestSuite()
	for test_suite in test_suites:
		suite.addTest(test_suite)
	return suite

def unit_case_suite(*test_cases):
	""" Create a unit testsuite containing the given unit testcases.
	@param test_cases: Subclasses of unittest.TestCase.
	@return: The new testsuite
	@rtype: unittest.TestSuite
	"""
	suite = unittest.TestSuite()
	for t in test_cases:
		suite.addTest(unittest.makeSuite(t))
	return suite

def unit_mod_suite(*modules):
	""" Create a unit testsuite containing the given test-modules.
	@param modules: Modules or objects with a suite() method which returns
			a unittest.TestSuite object.
	@return: The new testsuite.
	@rtype: unittest.TestSuite
	"""
	suite = unittest.TestSuite()
	for mod in modules:
		suite.addTest(mod.suite())
	return suite


def run_suite(suite):
	""" Run a test-suite.
	Provides a command-line interface for testing of a suite. Normally this
	will be placed in the bottom of a module like in the example at the
	top.
	"""
	from optparse import OptionParser

	parser = OptionParser()
	parser.add_option("-q", "--quiet",
					action="store_const", dest="verbosity", const=0,
					help="Only print statistics.")
	parser.add_option("-v", "--verbose",
					action="store_const", dest="verbosity", const=2,
					help="print info about evert test run.")
	parser.set_defaults(verbosity=1)
	(options, args) = parser.parse_args()

	if options.verbosity == 0:
		out = StringIO()
	else:
		out = sys.stdout

	testrunner = unittest.TextTestRunner(stream=out, verbosity=options.verbosity)
	results = testrunner.run(suite)

	if options.verbosity == 0:
		if results.wasSuccessful():
			print "SUCCESS :)"
		else:
			for failure in results.failures:
				print "FAIL:", failure[0]
			for error in results.errors:
				print "ERROR:", error[0]
