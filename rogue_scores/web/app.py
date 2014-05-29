# -*- coding: UTF-8 -*-

"""
This is a Web server for an online Rogue leaderboard. This is a Flask
application with a couple helpers to parse POST'ed scores.

There's currently no limit on the number of scores to store, and these are
stored in a local JSON file. You can set the directory used for this file (by
default it's the current one) with ``ROGUE_SCORES_PATH``.
"""

import os
import json
import logging
from flask import Flask, Response, render_template, request
from logging import FileHandler

from . import stats, store

app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SCORES'] = os.environ.get('ROGUE_SCORES_PATH', '.') \
    + '/_rogue-scores.json'

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(FileHandler('rogue_scores.log'))

@app.route("/")
def index():
    store.init_scores(app.config['SCORES'])
    hostname = request.headers.get('Host')
    with open(app.config['SCORES'], 'r') as f:
        s_all = json.loads(f.read())
        # display only the first 20 scores
        s = [dict(zip(('user', 'score', 'text'), l)) for l in s_all[:20]]
        return render_template('main.html', scores=s,
                               hostname=hostname,
                               stats=stats.stats(s_all))


@app.route('/scores', methods=['POST'])
def scores_upload():
    try:
        scores = json.loads(request.form['scores'])
    except ValueError as e:
        app.logger.error(e)
        return 'wrong json'

    app.logger.debug("Got some JSON")
    store.merge_scores(scores, app.config['SCORES'])
    return 'ok'

@app.route('/scores', methods=['GET'])
def scores_json():
    with open(app.config['SCORES']) as f:
        return Response(f.read(), 200, mimetype='application/json')
