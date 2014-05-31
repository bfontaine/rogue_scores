# -*- coding: UTF-8 -*-

"""
This modules helps computing interesting stats about the scores stored on the
Web server.
"""

import re
from collections import defaultdict

def stats(scores):
    """
    Compute stats on a ``ScoresStore``, and return a dict that can then be used
    in a template. Each value is a string, and current keys are:

        - ``max_level``: higher level, with the corresponding user
        - ``most_active``: most games played by one user
        - ``best_killer``: monster with the most kills

    If multiple users or monsters match a criteria for one of these keys, only
    one of them will be picked.
    """
    if not scores:
        return {}

    users   = defaultdict(int)
    killers = defaultdict(int)
    maxlvl = 0
    maxlvl_user = None

    for s in scores:
        users[s.user] += 1

        if s.status == 'killed' and s.cause:
            killers[s['cause']] += 1
        if s.level > maxlvl:
            maxlvl = s.level
            maxlvl_user = '%d (%s)' % (maxlvl, s.user)

    s = {
        'max_level': maxlvl_user
    }

    if users:
        s['most_active'] = \
            '%s (%d games)' % tuple(max(users.items(), key=lambda p: p[1]))
    else:
        s['most_active'] = '?'

    if killers:
        s['best_killer'] = \
            '%s (%d kills)' % tuple(max(killers.items(), key=lambda p: p[1]))
    else:
        s['best_killer'] = '?'


    return s
