# -*- coding: UTF-8 -*-

import os
import os.path
import json
import platform
import tempfile

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import rogue_scores.web
from rogue_scores.web import init_scores, sanitize_score, \
        sanitize_scores, merge_scores, index, scores_upload

class FakeRequest(object):
    scores = '[]'

    def __init__(self, *args, **kwargs):
        self.form = {'scores': FakeRequest.scores}


class TestRogueWeb(unittest.TestCase):

    def setUp(self):
        self._scores = rogue_scores.web.app.config['SCORES']
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        rogue_scores.web.app.config['SCORES'] = self.tmp.name

    def tearDown(self):
        rogue_scores.web.app.config['SCORES'] = self._scores
        if os.path.isfile(self.tmp.name):
            os.unlink(self.tmp.name)

    # == .init_scores == #

    def test_init_scores(self):
        os.unlink(self.tmp.name)
        self.assertFalse(os.path.isfile(self.tmp.name))
        init_scores()
        self.assertTrue(os.path.isfile(self.tmp.name))
        with open(self.tmp.name) as f:
            self.assertEquals('[]', f.read())

    # == .sanitize_score == #

    def test_sanitize_score_wrong_types(self):
        self.assertSequenceEqual(('12', 0, '25'),
                                 sanitize_score((12, None, 25)))
        self.assertSequenceEqual(('', 0, 'foo'),
                                 sanitize_score(({}, 'hello', ['foo'])))

    def test_sanitize_score_special_chars(self):
        self.assertSequenceEqual(('fooc', 25, 'killed.'),
                                 sanitize_score(('foo@c', 25, 'killed<.$@')))

    def test_sanitize_score(self):
        self.assertSequenceEqual(('foo', 25, 'killed.'),
                                 sanitize_score(('foo', 25, 'killed.')))

    # == .sanitize_scores == #

    def test_sanitize_scores_empty_list(self):
        self.assertSequenceEqual([], sanitize_scores([]))

    def test_sanitize_scores_remove_null_scores(self):
        self.assertSequenceEqual([], sanitize_scores([('foo', 0, 'bar')]))

    def test_sanitize_scores_remove_negative_scores(self):
        self.assertSequenceEqual([], sanitize_scores([('foo', -3, 'bar')]))

    def test_sanitize_scores_remove_empty_usernames(self):
        self.assertSequenceEqual([], sanitize_scores([('', 42, 'bar')]))

    def test_sanitize_scores_remove_bad_usernames(self):
        self.assertSequenceEqual([], sanitize_scores([('$@', 42, 'bar')]))

    def test_sanitize_scores(self):
        self.assertSequenceEqual([('a', 42, 'b')],
                                 sanitize_scores([('a', 42, 'b')]))


class TestRogueWebScoresMerging(unittest.TestCase):

    def setUp(self):
        self._scores = rogue_scores.web.app.config['SCORES']
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        rogue_scores.web.app.config['SCORES'] = self.tmp.name
        self.tmp.write(json.dumps([
            ['foo', 42, 'bar'],
            ['foo', 41, 'qux'],
            ['foo', 41, 'qax'],
            ['moo', 25, 'qwe']
        ]))
        self.tmp.close()

    def tearDown(self):
        rogue_scores.web.app.config['SCORES'] = self._scores
        if os.path.isfile(self.tmp.name):
            os.unlink(self.tmp.name)

    def getScores(self):
        with open(self.tmp.name) as f:
            return json.loads(f.read())

    # == .merge_scores == #

    def test_merge_scores_create_file(self):
        os.unlink(self.tmp.name)
        merge_scores([])
        self.assertTrue(os.path.isfile(self.tmp.name))

    def test_merge_scores_empty_list(self):
        initial = self.getScores()
        merge_scores([])
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_wrong_scores(self):
        initial = self.getScores()
        merge_scores([
            ('@$', 300, 'lolz'),
            ('me', -50, 'im a hackerz'),
        ])
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_no_duplicates(self):
        initial = self.getScores()
        merge_scores([('foo', 42, 'bar')])
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_at_the_end(self):
        initial = self.getScores()
        merge_scores([('foo', 1, 'bar')])
        self.assertSequenceEqual(['foo', 1, 'bar'], self.getScores()[-1])

    def test_merge_scores_same_user_score_but_different_text(self):
        initial = self.getScores()
        merge_scores([('foo', 42, 'barz')])
        scs = self.getScores()
        self.assertSequenceEqual(['foo', 42, 'barz'], scs[0])
        self.assertSequenceEqual(['foo', 42, 'bar'], scs[1])

    def test_merge_scores(self):
        initial = self.getScores()
        merge_scores([('wxs', 35, 'zzz')])
        scs = self.getScores()
        self.assertSequenceEqual(['wxs', 35, 'zzz'], scs[3])

class TestRogueWebRoutes(unittest.TestCase):

    def setUp(self):
        self._scores = rogue_scores.web.app.config['SCORES']
        self._req = rogue_scores.web.request
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        rogue_scores.web.app.config['SCORES'] = self.tmp.name
        self.tmp.write(json.dumps([
            ['foo', 42, 'bar'],
            ['moo', 25, 'qwe']
        ]))
        self.tmp.close()

    def tearDown(self):
        rogue_scores.web.app.config['SCORES'] = self._scores
        rogue_scores.web.request = self._req
        if os.path.isfile(self.tmp.name):
            os.unlink(self.tmp.name)

    def getScores(self):
        with open(self.tmp.name) as f:
            return json.loads(f.read())

    # == .index == #

    def test_index_no_score(self):
        os.unlink(self.tmp.name)
        with rogue_scores.web.app.app_context():
            ret = index()
        self.assertRegexpMatches(ret, r'</th>\s*</tr>\s*</table>')

    # == .scores_upload == #

    def test_scores_upload_wrong_json(self):
        FakeRequest.scores = '}w$'
        rogue_scores.web.request = FakeRequest()
        with rogue_scores.web.app.app_context():
            ret = scores_upload()
        self.assertEquals('wrong json', ret)

    def test_scores_upload_no_scores(self):
        FakeRequest.scores = '[]'
        rogue_scores.web.request = FakeRequest()
        with rogue_scores.web.app.app_context():
            ret = scores_upload()
        self.assertEquals('ok', ret)

    def test_scores_upload_new_scores(self):
        FakeRequest.scores = '[["myname", 455, "killed"]]'
        rogue_scores.web.request = FakeRequest()
        with rogue_scores.web.app.app_context():
            ret = scores_upload()
        self.assertEquals('ok', ret)
        self.assertSequenceEqual(('myname', 455, 'killed'),
                                 self.getScores()[0])
