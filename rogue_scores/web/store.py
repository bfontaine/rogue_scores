# -*- coding: UTF-8 -*-

"""
This modules provides functions to deal with scores stored on the Web server
"""

import os.path
import re
import json

class Score(object):
    def __init__(self, **kwargs):
        self.level = self.score = 0
        self.user = self.cause = self.monster = None
        self.__dict__.update(kwargs)

    def __int__(self):
        return self.level

    def __eq__(self):

    def json(self):
        return json.dumps(self.__dict__)

    def dump(self):
        return self.json()

    def load(data):
        ls = json.loads(data)
        return list(map(Score, ls))


class ScoresStore(object):
    """
    A scores store
    """
    __slots__ = ['path', 'scores', 'saved']

    def __init__(self, path, **kwargs):
        """
        Create a new store in the given file path. The file is created if it
        doesn't exist.
        """
        self.path = path
        self.scores = []
        self.saved = True
        if not os.path.isfile(self.path):
            dirname = os.path.dirname(self.path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            with open(self.path, 'w') as f:
                f.write(json.dumps(self.scores))
        else:
            self.scores = json.loads(self.path)

    def save(self):
        """
        Save the current scores
        """
        self.saved = True
        with open(self.path, 'w') as f:
            f.write(json.dumps(self.scores))

    def _insert(self, s):
        """
        Insert a score.
        """
        # TODO: we need to insert at the right place, and return False if
        # the score is already there

        idx = 1
        for i,s1 in enumerate(self.scores):
            idx = i+1
            if s1.score < s.score:
                break

        self.scores.insert(idx, s)
        self.saved = False

    def _add(self, s, **attrs):
        """
        Add a score. This is an internal function, use ``add`` instead. It
        returns ``True`` if the score has been added, ``False`` instead.
        """
        attrs.update(dict(s))

        if 'cause' not in attrs and 'text' in attrs:
            attrs['status'], attrs['level'], attrs['cause'] = \
                parse_text(attrs['text'])

        # sanitize the score & level
        try:
            attrs['score'] = int(attrs.get('score', 0))
            attrs['level'] = int(attrs.get('level', 0))
        except:
            return False

        if attrs['score'] <= 0 or attrs['level'] <= 0:
            return False

        # sanitize username, status, cause, monster
        user = re.sub(r'\W+', '', attrs['user'])
        for s in ('status', 'cause', 'monster'):
            if attrs[s] is not None:
                attrs[s] = re.sub(r'[^a-z]+', '', str(attrs[s]))

        return self._insert(Score(**attrs))

    def add(self, *scs, **kwargs):
        """
        Add one or more scores to the store. These are sanitized before
        insertion, and missing informations are added via parsing if possible.
        It returns the number of inserted items
        """
        ct = 0
        for s in scs:
            if self._add(s, **kwargs):
                ct += 1

        return ct

    def __del__(self):
        if not self.saved:
            self.save()

