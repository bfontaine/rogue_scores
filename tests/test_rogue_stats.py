# -*- coding: UTF-8 -*-

import platform
import subprocess

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.web.stats import parse_score, stats

class TestRogueScoresStats(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # == .parse_score == #

    def test_parse_score_wrong_text(self):
        self.assertEquals({'user':'foo', 'score':42, 'cause':None, 'level':0},
                          parse_score(('foo', 42, 'qsze ddz teefz z')))

    def test_parse_score_unknown_cause(self):
        self.assertEquals({'user':'foo', 'score':42, 'cause':None, 'level':17},
                          parse_score(('foo', 42, 'killed on level 17.')))

    def test_parse_score(self):
        expected = {'user': 'foo', 'score': 42, 'cause': 'qux', 'level': 3}
        d = parse_score(('foo', 42, 'killed on level 3 by a qux.'))
        self.assertEquals(expected, d)

    # == .stats == #

    def test_stats_no_scores(self):
        self.assertEquals({}, stats([]))

    def test_stats_one_score_no_level_nor_cause(self):
        self.assertEquals({
            'most_active': 'foo (1 games)',
            'max_level': None,
            'best_killer': '? (1 kills)',
        }, stats([('foo', 17, 'killed.')]))

    def test_stats_one_score_no_cause(self):
        self.assertEquals({
            'most_active': 'foo (1 games)',
            'max_level': '32 (foo)',
            'best_killer': '? (1 kills)',
        }, stats([('foo', 17, 'killed on level 32.')]))
