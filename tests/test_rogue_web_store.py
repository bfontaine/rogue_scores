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

from rogue_scores.web import store
from rogue_scores.web.store import init_scores, sanitize_score, \
        sanitize_scores, merge_scores

class TestRogueWebStore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.scores = self.tmp.name

    def tearDown(self):
        if os.path.isfile(self.scores):
            os.unlink(self.scores)

    # == .init_scores == #

    def test_init_scores_with_dir_without_file(self):
        os.unlink(self.scores)
        self.assertFalse(os.path.isfile(self.scores))
        init_scores(self.scores)
        self.assertTrue(os.path.isfile(self.scores))
        with open(self.scores) as f:
            self.assertEquals('[]', f.read())

    def test_init_scores_with_dir_with_file(self):
        s = 's$@%r9'
        with open(self.scores, 'w') as f:
            f.write(s)
        init_scores(self.scores)
        with open(self.scores) as f:
            self.assertEquals(s, f.read())

    def test_init_scores_without_dir(self):
        path = tempfile.mkdtemp()
        os.rmdir(path)
        self.assertFalse(os.path.exists(path))
        name = '%s/scores' % path
        init_scores(name)
        self.assertTrue(os.path.isdir(path))
        self.assertTrue(os.path.isfile(name))
        with open(name) as f:
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
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.scores = self.tmp.name
        self.tmp.write(json.dumps([
            ['foo', 42, 'bar'],
            ['foo', 41, 'qux'],
            ['foo', 41, 'qax'],
            ['moo', 25, 'qwe']
        ]).encode('utf-8'))
        self.tmp.close()

    def tearDown(self):
        if os.path.isfile(self.scores):
            os.unlink(self.scores)

    def getScores(self):
        with open(self.scores) as f:
            return json.loads(f.read())

    # == .merge_scores == #

    def test_merge_scores_create_file(self):
        os.unlink(self.scores)
        merge_scores([], self.scores)
        self.assertTrue(os.path.isfile(self.scores))

    def test_merge_scores_empty_list(self):
        initial = self.getScores()
        merge_scores([], self.scores)
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_wrong_scores(self):
        initial = self.getScores()
        merge_scores([
            ('@$', 300, 'lolz'),
            ('me', -50, 'im a hackerz'),
        ], self.scores)
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_no_duplicates(self):
        initial = self.getScores()
        merge_scores([('foo', 42, 'bar')], self.scores)
        self.assertSequenceEqual(initial, self.getScores())

    def test_merge_scores_at_the_end(self):
        initial = self.getScores()
        merge_scores([('foo', 1, 'bar')], self.scores)
        self.assertSequenceEqual(['foo', 1, 'bar'], self.getScores()[-1])

    def test_merge_scores_same_user_score_but_different_text(self):
        initial = self.getScores()
        merge_scores([('foo', 42, 'barz')], self.scores)
        scs = self.getScores()
        self.assertSequenceEqual(['foo', 42, 'barz'], scs[0])
        self.assertSequenceEqual(['foo', 42, 'bar'], scs[1])

    def test_merge_scores(self):
        initial = self.getScores()
        merge_scores([('wxs', 35, 'zzz')], self.scores)
        scs = self.getScores()
        self.assertSequenceEqual(['wxs', 35, 'zzz'], scs[3])
