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

r""" A general data model definition system.



Model
=====
	A model defines a data structure. This datastructure can be:
		- manipulated and validated.
		- used to create database tables
		- used to generate forms
		- and anything else you need validatable data stuctures for.

	A model is a dict where each value is an instances of
	L{field.interface.Field}.


	An example
	----------
	>>> personmodel = dict(
	... 	name = String(30),
	... 	birthdate = Datetime(),
	... 	iq = Int(),
	... 	about = Text()
	... )

	Above is a model defining a person. The field-types (String, Datetime, ..)
	are simply classes that provides validation. The following sections
	show what the model can be used for.


Manipulator
===========
	The model only defines a structure. When you want to manipulate data
	conforming to this structure, you use manipulators. The
	L{data.Manip} class is a easy-to-use interface for
	data manipulation. It provides data manipulation and validation.

		>>> from datetime import datetime
		>>> m = data.Manip(personmodel)
		>>> m.name = "John"
		>>> m.birthdate = datetime(1981, 12, 10, 21, 12)
		>>> m.iq = 110
		>>> m.about = "My name is John"

	As you can see, the data can easily be manipulated. But of course, we
	also want to validate the input.

		>>> m.validate()  # we have no invalid data in the manipulator
		>>> m.iq = "wrong"
		>>> m.validate()
		Error..



Datasources
===========
	A datasource is a interface for referencing data. The datasource
	can be a simple list in memory, a database, a text file or anything
	you might imagine. Datasources are used with the two fields defined
	in L{ds}: L{ds.One} and L{ds.Many}.

	One is used to define a reference to only a single element in
	a datasource. So if the datasource is the list (1, 2, 3),
	a One field would only be able to contain one of the three values.

	Many defines a reference to many elements in a datasource.


	Example
	-------

	>>> some_people = dsources.List(["john", "jack", "amy", "fry",
	... 		"peter", "leela"])
	>>> personmodel["bestfriend"] = ds.One(some_people)
	>>> personmodel["friends"] = ds.Many(some_people)

	>>> m = data.Manip(personmodel)
	>>> m.bestfriend = "amy"
	>>> m.friends = "fry", "leela"



Database
========
	The interface can be used to work with databases. The principle
	is simple. A model defines a database table. Datasources are
	used to define foreign and many-to-many relationships. Data is
	manipulated and validated using manipulators, and database
	interraction is done using the database api.

	After reading about form generation and parsing below, you will
	understand that this makes a very common use-case like: 
		- getting data from a database.
		- put the data in a form.
		- validate form input and store it in the database.
	into only a few lines of code.



Form generation and parsing
===========================
	You can generate forms from a model. There is a form generation
	interface in L{formgen}. Forms are explained in depth there.
	But we will explain the principle here.

	Since a model is a dictionary of well defined types (fields),
	representing it as a form is trival. When you get user input
	from the form, you can manipulate it by passing the input
	into a new manipulator (which can be validated).
"""


__all__ = ["formgen", "data", "datasource", "util",
		"dsources", "field"]
