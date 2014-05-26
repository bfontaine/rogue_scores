# -*- coding: UTF-8 -*-

import platform

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import rogue_scores

class TestRogueScoreUpload(unittest.TestCase):

    def setUp(self):
        pass

