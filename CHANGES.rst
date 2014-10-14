v0.1.0 (upcoming version)
-------------------------

- favicon added on the web page

v0.0.9 (03/06/2014)
-------------------

All changes of this version are in the upload script.

- support for ``ROGUE_SCORES_SERVER``
- ``--version`` flag support
- redirections are now followed
- User-Agent header added

v0.0.8 (31/05/2014)
-------------------

This release fixes a problem in the previous version where the limit of 20
scores has been removed.

v0.0.7 (31/05/2014)
-------------------

This is a breaking change on the server side API, but is fully compatible with
previous upload script versions. Unless you have Python code relying on
``rogue_scores.web``'s functions, it's ok to upgrade.

- more log messages on the server side
- stats added on the Web page
- ``/scores`` now serves the JSON scores file, and ``/scores?pretty`` serves a
  pretty-printed version
- ``rogue_scores.web`` moved to ``rogue_scores.web.app``
- scores-related functions moved from ``web`` to ``web.store``, with ``Score``
  and ``ScoresStore`` classes
- scores are now internally stored as JSON objects instead of list
- the Web page now shows each score's level, status and cause.

v0.0.6 (27/05/2014)
-------------------

- ``ROGUE_SCORES_PATH`` support
- the default Web scores file location is now the current directory

v0.0.5 (27/05/2014)
-------------------

- ``http[s]`` is not mandatory anymore when entering the remote server
- help text added on the Web index page

v0.0.4 (26/05/2014)
-------------------

- local server name file parsing fixed

v0.0.3 (26/05/2014)
-------------------

- default Web scores file location moved to ``~/.rogue-scores.json``
- logging added

v0.0.2 (26/05/2014)
-------------------

- dependencies list fixed

v0.0.1 (26/05/2014)
-------------------

- initial release
