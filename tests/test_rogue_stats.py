# -*- coding: UTF-8 -*-

import platform
import subprocess

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.web.store import ScoresStore
from rogue_scores.web.stats import stats

class TestRogueScoresStats(unittest.TestCase):

    def setUp(self):
        self.store = ScoresStore()

    # == .stats == #

    def test_stats_no_scores(self):
        self.assertEquals({}, stats([]))

    def test_stats_one_score_no_level_nor_cause(self):
        self.store.add({'user': 'foo', 'score': 17, 'status': 'killed'})

        self.assertEquals({
            'most_active': 'foo (1 games)',
            'max_level': None,
            'best_killer': '?',
        }, stats(self.store))

    def test_stats_one_score_no_cause(self):
        self.store.add({'user': 'foo', 'score': 17,
                        'status': 'killed', 'level': 32})
        self.assertEquals({
            'most_active': 'foo (1 games)',
            'max_level': '32 (foo)',
            'best_killer': '?',
        }, stats(self.store))

    def test_stats(self):
        self.store.add({'user': 'foo', 'score': 17, 'cause': 'a',
                        'status': 'killed', 'level': 21},
                       {'user': 'bar', 'score': 25, 'cause': 'a',
                        'status': 'killed', 'level': 32},
                       {'user': 'bar', 'score': 3, 'cause': 'b',
                        'status': 'killed', 'level': 2})
        self.assertEquals({
            'most_active': 'bar (2 games)',
            'max_level': '32 (bar)',
            'best_killer': 'a (2 kills)',
        }, stats(self.store))
