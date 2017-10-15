==================================================
boardgamegeek - A Python API for boardgamegeek.com
==================================================

.. note::

   The documentation is a work in progress. You can check out the unit tests for examples on how to use the library.


Introduction
============


``boardgamegeek`` is a Python library which makes it easy to access data from BoardGameGeek_ using their official XML
API.

It's an almost completely rewritten fork of libBGG_.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   changelog
   modules

Features
========

This library exposes (as Python objects with properties) the following BoardGameGeek_ entities:

* Users
* Games
* User collections
* Player guilds
* Plays
* Hot items

requests-cache_ is used for locally caching replies in order to reduce the amount of requests sent to the server.

.. note::
    The cache is enabled by default and it's configured to use memory only. It's also possible to use SQLite for a
    persistent cache.


Quick Install
=============

To install ``boardgamegeek``, just use pip::

    > pip install boardgamegeek


Usage
=====

Here's a quick usage example:

.. code-block:: pycon

    >>> from boardgamegeek import BGGClient
    >>> bgg = BGGClient()
    >>> g = bgg.game("Android: Netrunner")
    >>> g.name
    'Android: Netrunner'
    >>> g.id
    124742
    >>> for n in g.alternative_names: print n.encode("utf-8")
    ...
    安卓纪元：矩阵潜袭


To Do
=====

* Not all the information exposed by the official API is stored into the Python objects. Need to improve this.
* Try to support the other sites from the boardgamegeek's family
* Allow better control for configuring the cache
* Improve documentation :)


Contributions/suggestions are welcome!

Credits
=======

Original authors:

* Phil S. Stein (github:philsstein)
* Geoff Lawler (github:glawler)

Contributions to this fork:

* Tom Usher (github:tomusher)
* Brent Ropp (github:bar350)
* Michał Machnicki (github:machnic)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _BoardGameGeek: http://www.boardgamegeek.com
.. _libBGG: https://github.com/philsstein/libBGG
.. _requests-cache: https://pypi.python.org/pypi/requests-cache
