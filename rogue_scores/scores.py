# -*- coding: UTF-8 -*-

import re
import subprocess

def parse_line(l):
    """
    Parse a line from the scores and return the score as a tuple containing the
    user's name, score, and result.

    >>> parse_line(' 1   783 baptiste: killed on level 8 by a centaur.')
    ('baptiste', 783, 'killed on level 8 by a centaur.')
    """
    parts = re.split(r'\s+', l.strip(), 3)[1:]
    parts[1] = re.sub(r':$', '', parts[1])  # username

    return (parts[1], int(parts[0]), parts[2])

def get_scores(command='rogue'):
    """
    Return an ordered list of local user scores
    """
    p = subprocess.Popen([command, '-s'], stdout=subprocess.PIPE)
    lines = p.stdout.readlines()[2:]
    return [parse_line(l) for l in lines]
