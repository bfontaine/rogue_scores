rogue_scores
============

``rogue_scores`` is an online Rogue_ leaderboard as well as a script to upload
local user scores to it. Once installed, you only have to run ``rogue_scores``
and the script will upload your scores for you.

The script will ask you which server to use the first time you'll start it and
remember this choice. You can override the remembered choice by setting the
``ROGUE_SCORES_SERVER`` environment variable, or delete
``~/.rogue-scores-server`` to remove the script's remembered choice.

.. _Rogue: https://en.wikipedia.org/wiki/Rogue_(video_game)

Install
-------

With ``pip``: ::

    [sudo] pip install rogue_scores

Guide
-----

.. toctree::
   :maxdepth: 2

   api_reference
   changes
