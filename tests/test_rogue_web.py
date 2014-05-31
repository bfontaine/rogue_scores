# -*- coding: UTF-8 -*-

import os
import os.path
import json
import platform
import tempfile
import logging

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.web import app
from rogue_scores.web.app import index, scores_upload, scores_json

class FakeRequest(object):
    scores = '[]'

    def __init__(self, *args, **kwargs):
        self.form = {'scores': FakeRequest.scores}
        self.headers = {}
        self.args = {}

app.app.logger.handlers = [logging.FileHandler('/dev/null')]

class TestRogueWeb(unittest.TestCase):

    def setUp(self):
        self._scores = app.app.config['SCORES']
        self._req = app.request
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        app.request = FakeRequest()
        app.app.config['SCORES'] = self.tmp.name
        self.json = json.dumps([
            {'user': 'foo', 'level': 42, 'cause': 'bar',
             'status': 'killed', 'score': 24},
            {'user': 'moo', 'level': 25, 'cause': 'qwe',
             'status': 'killed', 'score': 255}
        ]).encode('utf-8')
        self.tmp.write(self.json)
        self.tmp.close()

    def tearDown(self):
        app.app.config['SCORES'] = self._scores
        app.request = self._req
        if os.path.isfile(self.tmp.name):
            os.unlink(self.tmp.name)

    def getScores(self):
        with open(self.tmp.name) as f:
            return json.loads(f.read())

    # == .index == #

    def test_index_no_score(self):
        os.unlink(self.tmp.name)
        with app.app.app_context():
            ret = index()
        self.assertRegexpMatches(ret, r'</th>\s*</tr>\s*</table>')

    # == .scores_upload == #

    def test_scores_upload_wrong_json(self):
        FakeRequest.scores = '}w$'
        app.request = FakeRequest()
        with app.app.app_context():
            ret = scores_upload()
        self.assertEquals('wrong json', ret)

    def test_scores_upload_no_scores(self):
        FakeRequest.scores = '[]'
        app.request = FakeRequest()
        with app.app.app_context():
            ret = scores_upload()
        self.assertEquals('ok', ret)

    def test_scores_upload_new_scores(self):
        FakeRequest.scores = '[["myname", 50, "killed by a foo on level 43"]]'
        app.request = FakeRequest()
        with app.app.app_context():
            ret = scores_upload()
        self.assertEquals('ok', ret)
        d = {'user': 'myname', 'level': 43,
             'status': 'killed', 'cause': 'foo', 'score': 50}
        self.assertEquals(d, self.getScores()[0])

    # == .scores_json == #

    def test_scores_json(self):
        with app.app.app_context():
            resp = scores_json()
        self.assertEquals(json.loads(self.json.decode('utf-8')),
                          json.loads(resp.data.decode('utf-8')))

    def test_scores_pretty_json(self):
        app.request = self._req
        with app.app.test_request_context('/scores?pretty=1'):
            resp = scores_json()
        txt = resp.data.decode('utf-8')
        self.assertEquals(json.loads(self.json.decode('utf-8')),
                          json.loads(txt))
        self.assertRegexpMatches(txt, '^\[\n +\{')
