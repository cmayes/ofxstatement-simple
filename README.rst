~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Simple plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://img.shields.io/travis/cmayes/ofxstatement-simple.svg
        :target: https://travis-ci.org/cmayes/ofxstatement-simple

.. image:: https://img.shields.io/pypi/v/ofxstatement-simple.svg
        :target: https://pypi.python.org/pypi/ofxstatement-simple

.. image:: https://coveralls.io/repos/cmayes/ofxstatement-simple/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/cmayes/ofxstatement-simple?branch=master


This is an `ofxstatement`_ plugin for `Simple`_ JSON statements downloaded
from the site. `ofxstatement`_ converts the JSON into a series of "check"
transactions in an OFX file.

.. _ofxstatement: https://github.com/kedder/ofxstatement
.. _Simple: https://www.simple.com/
.. _Moneydance: http://moneydance.com/

`ofxstatement`_ is a tool for converting proprietary bank statements into the
OFX format, suitable for importing into GnuCash, Moneydance, and other compatible
applications. The plugin for ofxstatement parses a particular proprietary bank
statement format and produces a common data structure that is then formatted
into an OFX file.

Requirements
============

As with `ofxstatement`_, this plugin requires Python 3.  You will need to have
`ofxstatement`_ installed; the package will be brought in as a dependency if
you install the plugin via `pip`_.

.. _pip: https://pypi.python.org/pypi/pip

Installation
============

You can install the plugin via most of the normal Python methods (be sure to
install using your environment's python3 installation). Remove the `--user`
option if you wish to install the package globally.

pip
---

::

  pip3 install --user ofxstatement-simple

setup.py
--------

::

  python3 setup.py install --user

Configuration
=============

Note that you can specify 'bank' and 'account' in ofxstatement's configuration file (accessible
using the `ofxstatement edit-config` command or directly at
`~/.local/share/ofxstatement/config.ini` (on Linux, at least).  Setting these values makes it
easier for your personal finance application to recognize which account the file's data
belongs to.

Also note that transactions for zero amounts are filtered by default.  If you wish to include
zero-amount transactions, set 'zero_filter' to 'false' in your settings.  Here is an example
of a settings block for the simple plugin::

  [simple]
  account = 8675309
  plugin = simple
  zero_filter = false

Usage
=====

Export your Simple transactions into a JSON file (it's currently
`<date>-exported_transactions.json`). Then run::

  $ ofxstatement convert -t simple <date>-exported_transactions.json simple.ofx

You can then import `simple.ofx` into the personal finance application of your choice.
