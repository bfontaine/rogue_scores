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
            ['foo', 42, 'bar'],
            ['moo', 25, 'qwe']
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
        FakeRequest.scores = '[["myname", 455, "killed"]]'
        app.request = FakeRequest()
        with app.app.app_context():
            ret = scores_upload()
        self.assertEquals('ok', ret)
        self.assertSequenceEqual(('myname', 455, 'killed'),
                                 self.getScores()[0])

    # == .scores_json == #

    def test_scores_json(self):
        with app.app.app_context():
            resp = scores_json()
        self.assertEquals(self.json, resp.data)

    def test_scores_pretty_json(self):
        FakeRequest.args = { 'pretty': None }
        with app.app.app_context():
            resp = scores_json()
        self.assertEquals(self.json, resp.data)
