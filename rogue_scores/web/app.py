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

from . import stats
from .store import ScoresStore

app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SCORES'] = os.environ.get('ROGUE_SCORES_PATH', '.') \
    + '/_rogue-scores.json'

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(FileHandler('rogue_scores.log'))


@app.route("/")
def index():
    count = request.args.get('count')
    try:
        count = max(int(count), 1)
    except:
        count = 20  # default
    store = ScoresStore(app.config['SCORES'])
    return render_template('main.html',
                           scores=store.get(count),
                           hostname=request.headers.get('Host'),
                           stats=stats.stats(store))


@app.route('/scores', methods=['POST'])
def scores_upload():
    try:
        scores = json.loads(request.form['scores'])
    except ValueError as e:
        app.logger.error(e)
        return 'wrong json'

    app.logger.debug("Got some JSON")
    store = ScoresStore(app.config['SCORES'])
    store.add(*scores)
    store.save()
    return 'ok'


@app.route('/scores', methods=['GET'])
def scores_json():
    store = ScoresStore(app.config['SCORES'])
    kwargs = {}
    if 'pretty' in request.args:
        kwargs['indent'] = 4
    return Response(store.json(**kwargs), 200, mimetype='application/json')
