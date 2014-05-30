# -*- coding: UTF-8 -*-

"""
This modules provides functions to deal with scores stored on the Web server
"""

import os.path
import re
import json

def parse_text(text):
    """
    Parse a score's text and return a dictionnary
    """
    # TODO

    # ^killed, ^died, ^quit
    # on level (\d+)
    # of ([a-z]+), by an? ([a-z]+), by ([a-z]+)

    return {}


class Score(object):
    def __init__(self, **kwargs):
        self.level = self.score = 0
        self.user = self.cause = self.status = None
        self.__dict__.update(kwargs)

    def json(self):
        return json.dumps(self.__dict__)

    def dump(self):
        return self.json()

    def load(data):
        ls = json.loads(data)
        return list(map(Score, ls))

    def __int__(self):
        return self.score

    def __eq__(self, o):
        if not isinstance(o, Score):
            return False

        for attr in ('level', 'score', 'user', 'cause', 'status'):
            if getattr(self, attr) != getattr(o, attr):
                return False

        return True

    def __gt__(self, o):
        return int(self) > int(o)

    def __ge__(self, o):
        return int(self) >= int(o)

    def __lt__(self, o):
        return int(self) < int(o)

    def __le__(self, o):
        return int(self) <= int(o)


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
        for i, s1 in enumerate(self.scores):
            if s == s1:
                return False
            if s > s1:
                self.scores.insert(i, s)
                break
        else:
            self.saved = False
            self.scores.append(s)
            return True

    def _add(self, s, **attrs):
        """
        Add a score. This is an internal function, use ``add`` instead. It
        returns ``True`` if the score has been added, ``False`` instead.
        """
        attrs.update(dict(s))

        if 'cause' not in attrs and 'text' in attrs:
            attrs.update(parse_text(attrs['text']))
            del attrs['text']

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
            if isinstance(s, tule) or isinstance(s, list):
                # old format
                s = {'user': s[0], 'score': s[1], 'text': s[2]}

            if self._add(s, **kwargs):
                ct += 1

        return ct

    def __del__(self):
        if not self.saved:
            self.save()
