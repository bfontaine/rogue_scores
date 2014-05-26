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
    name = app.config['SCORES']
    if not os.path.isfile(name):
        with open(name, 'w') as f:
            f.write(json.dumps([]))

def sanitize_scores(scs):
    # TODO
    return scs

def merge_scores(scs):
    init_scores()
    with open(app.config['SCORES'], 'r') as f:
        scores = json.loads(f.read())

    scs = [map(str, s) for s in scs]

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

        if s1[:2] == s2[:2]:
            # don't add duplicates in the file
            scs.pop(0)
            continue

        coll = scores if int(s1[1]) > int(s2[1]) else scs
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
    scores = sanitize_scores(json.loads(request.form['scores']))
    r = merge_scores(scores)
    return 'ok'

