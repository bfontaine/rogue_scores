# -*- coding: UTF-8 -*-
from __future__ import print_function

"""
This module defines the endpoint used to provide the ``rogue_scores`` script.
"""

import sys
import platform
import os.path
from .upload import post_scores
from .scores import get_scores

if platform.python_version() < '3.0':
    import urlparse
else:
    import urllib.parse as urlparse

SERVER_FILE = os.path.expanduser('~/.rogue-scores-server')


def set_server():
    """
    Ask the user for a server address and store it in a local file.
    """
    prompt = 'Which remote server do you want me to use? '
    if platform.python_version() < '3.0':
        r = raw_input(prompt)
    else:
        r = input(prompt)

    r = r.strip()

    if not r:
        print('You must provide a remote server address!')
        return set_server()

    if not r.startswith('http'):
        r = 'http://' + r

    u = urlparse.urlparse(r.strip())
    with open(SERVER_FILE, 'w') as f:
        f.write('%s' % u.netloc)


def run():
    """
    Run the command-line interface
    """
    if not os.path.isfile(SERVER_FILE):
        set_server()

    with open(SERVER_FILE) as f:
        server = f.readline().strip()

    scs = get_scores()

    if not scs:
        print("There're no scores to send.", file=sys.stderr)
        # this 'return' is here for tests where sys.exit is a mock
        return sys.exit(1)

    print("scs:", scs)
    if post_scores(scs, target=server):
        print("Scores posted with success!")
    else:
        print("An error occurred.", file=sys.stderr)
        print("I tried to send %d scores to '%s'." % (len(scs), server))
        sys.exit(2)
