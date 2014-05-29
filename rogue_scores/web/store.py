# -*- coding: UTF-8 -*-

"""
This modules provides functions to deal with scores stored on the Web server
"""

import os.path
import re
import json

class Score(object):
    __slots__ = ['user', 'score', 'level', 'text']

    def __init__(self, **kwargs):
        self.user  = attrs.get('user')
        self.score = attrs.get('score', 0)
        self.level = attrs.get('level', 0)
        self.text  = attrs.get('text')

    def __int__(self):
        return self.level

    def __eq__(self, other):
        return isinstance(other, Score) and self.json() == other.json()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return self.score.__le__(int(other))

    def __lt__(self, other):
        return self.score.__lt__(int(other))

    def __ge__(self, other):
        return self.score.__ge__(int(other))

    def __gt__(self, other):
        return self.score.__gt__(int(other))

    def json(self):
        return json.dumps({
            'user': self.user,
            'score': self.score,
            'level': self.level,
            'text': self.text,
        })

    def dump(self):
        return self.json()

    def load(data):
        ls = json.loads(data)
        return list(map(Score, ls))


def init_scores(name):
    """
    Initialize the local scores file
    """
    if not os.path.isfile(name):
        dirname = os.path.dirname(name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(name, 'w') as f:
            f.write(json.dumps([]))


def sanitize_score(sc):
    """
    Sanitize a score from an external source. The score should be a tuple of
    ``user``, ``score``, and ``text``.
    """
    u, s, t = sc[:3]

    try:
        s = int(s)
    except ValueError:
        s = 0
    except TypeError:
        s = 0

    u = re.sub(r'\W+', '', str(u).strip())[:40]
    t = re.sub(r'[^\w\., ]+', '', str(t))[:80]
    return (u, s, t)


def sanitize_scores(scs):
    """
    Sanitize scores from an external source, and filter out those with an empty
    username and a null score.
    """
    return [s for s in map(sanitize_score, scs) if s[0] and s[1] > 0]


def merge_scores(scs, fname):
    """
    Merge local scores with the given ones, and save the new list in the local
    file. Duplicate scores (same user, score and text) are not preserved, and
    if a new score is the same than a previous one, the previous one is taking
    precedence over the new one (i.e. it'll be the first in the leaderboard).
    """
    scs = list(map(list, sanitize_scores(scs)))
    scs.sort(key=lambda s: s[1], reverse=True)

    init_scores(fname)
    with open(fname, 'r') as f:
        scores = Score.load(f.read())

    final_scores = []
    while scores or scs:
        if not scores:
            final_scores += scs
            break

        if not scs:
            final_scores += scores
            break

        s1 = scores[0]
        s2 = scs[0]

        if s1 == s2:
            # don't add duplicates in the file
            scs.pop(0)
            continue

        coll = scores if s1[1] >= s2[1] else scs
        final_scores.append(coll.pop(0))

    with open(fname, 'w') as f:
        f.write(json.dumps(list(map(lambda s: s.dump(), final_scores))))
