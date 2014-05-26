# -*- coding: UTF-8 -*-

"""
Web server for ``rogue_scores``
"""

import os.path
import re
import json
from flask import Flask, render_template, request
app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SCORES'] = '_scores.txt'

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
    Sanitize a score from an external source. Its argument should be a tuple of
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
    return [s for s in map(sanitize_score, scs) if s[0] and s[1]>0]

def merge_scores(scs):
    """
    Merge local scores with the given ones, and save the new list in the local
    file.
    """
    scs = sanitize_scores(scs)

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
    with open(app.config['SCORES'], 'r') as f:
        s = json.loads(f.read())
        s = [{'user':l[0], 'score':l[1], 'text':l[2]} for l in s]
        return render_template('main.html', scores=s)

@app.route('/scores', methods=['POST'])
def scores_upload():
    try:
        scores = json.loads(request.form['scores'])
    except ValueError:
        return 'wrong json'
    merge_scores(scores)
    return 'ok'

