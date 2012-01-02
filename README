About
=====

Python library for web-development. It does not enforce any development model
or structure, but instead includes tools to simplify modern (web)development
trends like UNIT testing, WSGI, and XML.


Status
======

Enkel is quite usable on its own. It has been used by the project owners in
both commercial and open source projects. But it is not a well planned library.
It was created to solve specific problems often with quite a time-span between
related modules. So even though the modules are stable and provided with mostly
good api-documentation, it lacks in overall structure and logic.



Getting started
===============

The examples use bash/zsh shell compatible commands.
The library has only been tested on Linux, but should work on any
platform with python installed.



Requirements
------------

"lxml" and "setuptools".



Build translation files
-----------------------

~$ make mo


Run the testsuite
-----------------

Run the tests using (all should pass):

    ~$ python setup.py test

You can use:

    ~$ make clean

to remove the temporary files.



Install
=======


Install alt (1)
---------------

As root:

	~$ python setup.py install


Install alt (2): development/live mode
--------------------------------------

This is the best alternative if you use Bazaar to keep up-to-date.

Setuptools can be used to install the library in development mode.  
This actually just makes a link, so you can still update using ``bzr 
pull`` without having to reinstall.

Lets use ``~/devpy`` as our install folder:

	~$ mkdir ~/devpy
	~$ export PYTHONPATH="$PYTHONPATH:$HOME/devpy"
	~$ export PATH="$PATH:$HOME/devpy"
	~$ python setup.py develop -d ~/devpy

You should of course add the exports to your .bashrc/.zshrc or
similar.



Test the install
================

You can test the install like this:

	~$ cd
	~$ python -c "import enkel"

If no error message is displayed and the testsuite (above) passed, the
library should be working perfectly on your system.



Build apidocs
=============

Install pydoc (http://pydoc.sourceforge.net).

Run:

    ~$ make apidoc

If everything works you should be able to browse the apidocs by
pointing your browser to:

    apidoc/index.html
