#! /usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function

"""
Before ``rogue_scores`` v0.0.7, scores were stored as a list of lists, each
score being represented as a 3-items list: an username, a score and a text.
Starting from v0.0.7, scores are represented as objects, serialized as dicts.

This script takes a file with the old format and changes it to the actual
format.

Usage: ::

    python updatefmt <filepath>
"""

import sys
import json

def update(path):
    with open(path, 'r') as f:
        scores = json.loads(f.read())

    scores = [dict(zip(('user', 'score', 'text'), s)) for s in scores]
    with open(path, 'w') as f:
        f.write(json.dumps(scores))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:\n\t%s <file path>" % sys.argv[0])
        sys.exit(1)
    update(sys.argv[1])
