# -*- coding: UTF-8 -*-
from __future__ import print_function

"""
This is a Web server for an online Rogue leaderboard. This is a Flask
application with a couple helpers to parse POST'ed scores.

There's currently no limit on the number of scores to store, and these are
stored in a local JSON file.
"""

import os.path
import re
import json
import logging
from flask import Flask, render_template, request
from logging import FileHandler

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SCORES'] = os.path.expanduser('~/.rogue-scores.json')

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(FileHandler('rogue_scores.log'))


def init_scores():
    """
    Initialize the local scores file
    """
    name = app.config['SCORES']
    if not os.path.isfile(name):
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


def merge_scores(scs):
    """
    Merge local scores with the given ones, and save the new list in the local
    file. Duplicate scores (same user, score and text) are not preserved, and
    if a new score is the same than a previous one, the new one is taking
    precedence over the former one (i.e. it'll be the first in the
    leaderboard).
    """
    scs = list(map(list, sanitize_scores(scs)))
    scs.sort(key=lambda s: s[1], reverse=True)

    init_scores()
    with open(app.config['SCORES'], 'r') as f:
        scores = json.loads(f.read())

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

        coll = scores if s1[1] > s2[1] else scs
        final_scores.append(coll.pop(0))

    with open(app.config['SCORES'], 'w') as f:
        f.write(json.dumps(final_scores))


@app.route("/")
def index():
    init_scores()
    hostname = request.headers.get('Host')
    with open(app.config['SCORES'], 'r') as f:
        s = json.loads(f.read())
        s = [dict(zip(('user', 'score', 'text'), l)) for l in s]
        return render_template('main.html', scores=s, hostname=hostname)


@app.route('/scores', methods=['POST'])
def scores_upload():
    try:
        scores = json.loads(request.form['scores'])
    except ValueError as e:
        app.logger.error(e)
        return 'wrong json'

    app.logger.debug("Got some JSON")
    merge_scores(scores)
    return 'ok'
