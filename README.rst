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

Upgrade with: ::

    [sudo] pip install -U rogue_scores

Usage
-----

`Read the docs`_.

This repository is Dokku-ready: you just need to set up persistent storage to
not lose scores between deployments and it should run without anymore
configuration.

If you just want the upload script, install the package and run it: ::

    rogue_scores

It’ll ask you which server to use the first time, and remember it.

.. _Read the docs: http://rogue-scores.readthedocs.org

Contributing
------------

All contributions are welcomed. Please open an issue_ describing the problem as
well as your Python version and OS. If you can contribute code,
`fork this repo`_ and run ``make deps`` to set up your local environment. Use
``make check`` for simple tests and ``make check-versions`` for the full test
suite. If you can, add a failing test showing the bug. Commit your changes and
open a pull request on this repo.

.. _issue: https://github.com/bfontaine/rogue_scores/issues
.. _fork this repo: https://github.com/bfontaine/rogue_scores/fork
