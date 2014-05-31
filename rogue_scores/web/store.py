# -*- coding: UTF-8 -*-

"""
This modules provides functions to deal with scores stored on the Web server.
Each score is represented as a dict-like object, with the following keys:

    - ``level``
    - ``score``
    - ``user``: user's name
    - ``cause``: the monster's name if the user was killed, the death cause
      if the user died of starvation or hypothermia
    - ``status`` (``str``): ``died``, ``killed``, ``quit``

These keys can be ``None`` (or ``0`` for numerical ones) if the attribute is
not set.
"""

import os.path
import re
import json


def parse_text(text):
    """
    Parse a score's text and return a dictionnary of attributes: ``level``,
    ``status``, ``cause``. Only a subset of these attributes might be returned
    if the text couldn't be parsed or some of them aren't relevant.

    ``status`` can be either ``killed`` (by a monster), ``quit``, ``died``
    (e.g. of starvation) or ``won``. This function should work with multiple
    text variants.

    >>> parse_text("killed on level 12 by a quagga.")
    {'level': 12, 'status': 'killed', 'cause': 'quagga'}
    >>> parse_text("quit on level 3.")
    {'level': 3, 'status': 'quit'}
    >>> parse_text("died of hypothermia on level 6")
    {'level': 6, 'status': 'died', 'cause': 'hypothermia'}
    >>> parse_text("killed on level 3 by hypothermia.")
    {'level': 3, 'status': 'died', 'cause': 'hypothermia'}

    .. versionadded:: 0.0.7
    """
    text = text.strip().lower()
    attrs = {}
    m = re.match(r'.* on level (\d+).*', text)
    if m:
        attrs['level'] = int(m.groups(1)[0])

    if text.startswith('quit'):
        attrs['status'] = 'quit'
        return attrs

    m = re.match(r'died of ([a-z]+).*', text)
    if m:
        attrs['cause'] = m.groups(1)[0]
        attrs['status'] = 'died'
        return attrs

    if text.startswith('killed '):
        m = re.match('.* by an? ([a-z]+).*', text)
        if m:
            attrs['cause'] = m.groups(1)[0]
            attrs['status'] = 'killed'
            return attrs

        m = re.match('.* by ([a-z]+).*', text)
        if m:
            attrs['cause'] = m.groups(1)[0]
            attrs['status'] = 'died'
            return attrs

    if text.startswith('won '):
        attrs['status'] = 'won'

    return attrs


class BadScoreFormatException(Exception):
    """
    This exception is raised when a wrongly formatted score is given to a
    ``ScoresStore`` instance's ``add`` method.
    """
    def __init__(self, s):
        Exception.__init__(self, s or 'Unrecognized format: %s' % str(s))


class Score(object):
    """
    A score. This object implements some dict-like methods to provide an easy
    access to its attributes. It have at least these ones: ``level``, ``score``
    (default: ``0``), ``user``, ``status``, ``cause`` (default: ``None``).

    .. versionadded:: 0.0.7
    """

    def __init__(self, **kwargs):
        """
        Create a new score. Any attribute can be added via a keyword argument.
        """
        self.level = self.score = 0
        self.user = self.cause = self.status = None
        self.__dict__.update(kwargs)

    def __int__(self):
        return self.score

    def __eq__(self, o):
        if not isinstance(o, Score):
            return False

        for attr in ('level', 'score', 'user', 'cause', 'status'):
            if getattr(self, attr) != getattr(o, attr):
                return False

        return True

    def __ne__(self, o):
        return not self.__eq__(o)

    def __gt__(self, o):
        return int(self) > int(o)

    def __ge__(self, o):
        return int(self) >= int(o)

    def __lt__(self, o):
        return int(self) < int(o)

    def __le__(self, o):
        return int(self) <= int(o)

    def __getitem__(self, k):
        return self.__dict__[k]

    def __repr__(self):
        return 'Score(%s)' % str(self.__dict__)


class ScoresStore(object):
    """
    A scores store. This is based on a JSON file, but the interface should not
    depend on the underlying storage method.

    >>> s = ScoresStore('/tmp/foo')
    >>> s.add({'user': 'foo', 'level': 42, 'status': 'quit'})
    1
    >>> len(s)
    1
    >>> s.save()
    None

    .. versionadded:: 0.0.7
    """
    __slots__ = ['path', 'scores', 'saved']

    def __init__(self, path=None, **kwargs):
        """
        Create a new store in the given file path. The file is created if it
        doesn't exist. If ``path`` is ``None``, the store is not saved on disk.
        """
        self.path = path
        self.scores = []
        self.saved = True
        if self.path and not os.path.isfile(self.path):
            dirname = os.path.dirname(self.path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            self.save()
        else:
            self._load()

    def json(self, **kwargs):
        """
        Return a JSON representation of this store
        """
        return json.dumps(self.scores, default=lambda o: o.__dict__, **kwargs)

    def _load(self):
        """
        Load the store from its path, if it has one
        """
        if not self.path:
            return

        with open(self.path) as f:
            self.scores = json.loads(f.read())

        if len(self.scores) > 0 and isinstance(self.scores[0], list):
            # support for old format
            self.scores, scs = [], self.scores
            self.add(*scs)
            self.save()
        else:
            # get Score objects instead of dicts
            self.scores = list(map(lambda d: Score(**d), self.scores))

    def save(self):
        """
        Save the current scores on disk, if the store's ``path`` is not
        ``None``.
        """
        if self.path:
            self.saved = True
            with open(self.path, 'w') as f:
                f.write(self.json())

    def _insert(self, s):
        """
        Insert a score and return ``True`` if it was inserted or ``False`` if
        it wasn't because it's already there.
        """
        for i, s1 in enumerate(self.scores):
            if s == s1:
                return False
            if s > s1:
                self.scores.insert(i, s)
                break
        else:
            self.scores.append(s)
        self.saved = False
        return True

    def _add(self, s, **attrs):
        """
        Add a score. This is an internal function, use ``add`` instead. It
        returns ``True`` if the score has been added, ``False`` if not.
        """
        attrs.update(dict(s))

        user = re.sub(r'\W+', '', attrs.get('user', ''))
        if not user:
            return False
        else:
            attrs['user'] = user

        if 'cause' not in attrs and 'text' in attrs:
            attrs.update(parse_text(attrs['text']))
            del attrs['text']

        # sanitize the score & level
        try:
            attrs['score'] = int(attrs.get('score', 0))
            attrs['level'] = int(attrs.get('level', 0))
        except:
            return False

        if attrs['score'] <= 0 or attrs['level'] < 0:
            return False

        # sanitize status, cause, monster
        for s in ('status', 'cause', 'monster'):
            if attrs.get(s) is not None:
                attrs[s] = re.sub(r'[^a-z]+', '', str(attrs[s]))

        return self._insert(Score(**attrs))

    def add(self, *scs, **kwargs):
        """
        Add one or more scores to the store. These are sanitized before
        insertion, and missing informations are added via parsing if possible.
        It returns the number of inserted items. An item is not added if:

            - it's already present
            - it doesn't contain basic info on the score, like no user or a
              null score

        Keyword arguments can be used to set default values on all added
        scores.
        """
        ct = 0
        for s in scs:
            # old server format, and format sent by the upload script
            if not isinstance(s, dict):
                if (isinstance(s, list) or isinstance(s, tuple)) \
                        and len(s) == 3:
                    s = {'user': s[0], 'score': s[1], 'text': s[2]}
                else:
                    raise BadScoreFormatException(s)

            if self._add(s, **kwargs):
                ct += 1

        return ct

    def get(self, limit):
        """
        Return at most ``limit`` scores
        """
        return self.scores[:limit]

    def __iter__(self):
        for s in self.scores:
            yield s

    def __getitem__(self, i):
        return self.scores[i]

    def __len__(self):
        return len(self.scores)

    def __del__(self):
        if not self.saved:
            self.save()

    def __empty__(self):
        return not self.scores

    def __repr__(self):
        return 'ScoresStore(%s)' % str(list(self))
