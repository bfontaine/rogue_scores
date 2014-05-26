============
rogue_scores
============

.. image:: https://img.shields.io/travis/bfontaine/rogue_scores.png
   :target: https://travis-ci.org/bfontaine/rogue_scores
   :alt: Build status

.. image:: https://coveralls.io/repos/bfontaine/rogue_scores/badge.png?branch=master
   :target: https://coveralls.io/r/bfontaine/rogue_scores?branch=master
   :alt: Coverage status

.. image:: https://img.shields.io/pypi/v/rogue_scores.png
   :target: https://pypi.python.org/pypi/rogue_scores
   :alt: Pypi package

.. image:: https://img.shields.io/pypi/dm/rogue_scores.png
   :target: https://pypi.python.org/pypi/rogue_scores

``rogue_scores`` is an online Rogue_ leaderboard with its upload script.

.. _Rogue: https://en.wikipedia.org/wiki/Rogue_(video_game)

Install
-------

.. code-block::

    [sudo] pip install rogue_scores

The script as well as the Web server work with both Python 2.x and 3.x.

Usage
-----

`Read the docs`_.

This repository is Dokku-ready: just push it to your Dokku instance and it’ll
run without anymore configuration. It won’t work on Heroku because it uses a
local file to keep track of scores but that can be solved by using an external
database or an S3 instance.

.. _Read the docs: http://rogue-scores.readthedocs.org
