# -*- coding: UTF-8 -*-

import platform
import subprocess

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.cli import run

class TestRogueCLI(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # == .run == #

    def test_cli_run(self):
        pass  # TODO
