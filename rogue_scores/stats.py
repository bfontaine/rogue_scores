# -*- coding: UTF-8 -*-

"""
This modules helps computing interesting stats about the scores stored on the
Web server.
"""

import re
from collections import defaultdict

def parse_score(s):
    """
    parse a score and return a dict with the following keys: ``user``,
    ``score``, ``level``, ``cause``.
    """

    m = re.match(r'.*on level (\d+)', s[2])
    lvl = m.groups(1)[0] if m else 0

    m = re.match(r'killed.*by a (\w+)\.', s[2])
    cause = m.groups(1)[0] if m else None

    return {
        'user': s[0],
        'score': s[1],
        'cause': cause,
        'level': int(lvl),
    }

def stats(scores):
    """
    Compute stats on a list of scores, and return a dict that can then be used
    in a template.
    """
    if not scores:
        return {}

    users   = defaultdict(int)
    killers = defaultdict(int)
    maxlvl = 0
    maxlvl_user = None

    for s in scores:
        s = parse_score(s)
        users[s['user'] or '?'] += 1
        killers[s['cause'] or '?'] += 1
        if s['level'] > maxlvl:
            maxlvl = s['level']
            maxlvl_user = '%d (%s)' % (maxlvl, s['user'])

    most_active = max(users.items(), key=lambda p: p[1])
    best_killer = max(killers.items(), key=lambda p: p[1])

    most_active = '%s (%d games)' % tuple(most_active)
    best_killer = '%s (%d kills)' % tuple(best_killer)

    return {
        'most_active': most_active,
        'max_level': maxlvl_user,
        'best_killer': best_killer,
    }
