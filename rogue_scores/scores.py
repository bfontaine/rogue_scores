# -*- coding: UTF-8 -*-

"""
This module is used to get and parse local user scores.
"""

import re
import subprocess


def parse_line(l):
    """
    Parse a line from the scores given by Rogue and return a score as a tuple
    containing the user's name, score, and result. If the line wasn't correct,
    it returns ``None``.

    >>> parse_line(' 1   783 baptiste: killed on level 8 by a centaur.')
    ('baptiste', 783, 'killed on level 8 by a centaur.')
    """
    parts = re.split(r'\s+', str(l).strip(), 3)[1:]

    if len(parts) != 3:
        return None

    parts[1] = re.sub(r':$', '', parts[1])  # username

    try:
        return (parts[1], int(parts[0]), parts[2])
    except ValueError:
        return None


def get_scores(command='rogue'):
    """
    Return a list of local user scores, as given by the command ``rogue -s``.
    These scores should be ordered from the best score to the worst one, and
    limited to 10, but this limit is not enforced by the function.

    Keyword arguments:
            - ``command`` (``string``, default: ``rogue``): the command to use
              to run ``rogue``.
    """
    try:
        p = subprocess.Popen([command, '-s'], stdout=subprocess.PIPE)
    except OSError:
        return []
    lines = p.stdout.readlines()[2:]
    return [parse_line(l) for l in lines]
