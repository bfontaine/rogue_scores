# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.web import init_scores, sanitize_scores, merge_scores

class TestRogueWeb(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # == .init_scores == #
    # TODO
    # == .sanitize_scores == #
    # TODO
    # == .merge_scores == #
    # TODO

