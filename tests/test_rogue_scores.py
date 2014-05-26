# -*- coding: UTF-8 -*-

import platform
import subprocess

if platform.python_version() < '3.0':
    from StringIO import StringIO
else:
    from io import StringIO

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.scores import parse_line, get_scores

class FakePopen(object):
    def __init__(self, args, **kwargs):
        FakePopen.last_args = args
        self.stdout = StringIO(FakePopen.default_scores)

    default_scores = """\
Top Ten Scores:
   Score Name
 1   783 baptiste: killed on level 8 by a centaur.
 2   528 baptiste: killed on level 5 by a kestrel.
 3   404 baptiste: killed on level 3 by a hobgoblin.
 4   324 baptiste: killed on level 3 by a hobgoblin.
 5   305 baptiste: killed on level 2 by a hobgoblin.
 6   258 baptiste: killed on level 3 by a rattlesnake.
 7   231 baptiste: killed on level 3 by a kestrel.
 8   206 baptiste: killed on level 2 by a hobgoblin.
 9   172 baptiste: killed on level 2 by a kestrel.
10   163 baptiste: killed on level 2 by a hobgoblin."""

    last_args = None


class TestRogueScores(unittest.TestCase):

    def setUp(self):
        self._popen = subprocess.Popen
        subprocess.Popen = FakePopen

    def tearDown(self):
        subprocess.Popen = self._popen

    # == .parse_line == #

    def test_parse_line_not_a_string(self):
        self.assertEquals(None, parse_line(42))
        self.assertEquals(None, parse_line([]))
        self.assertEquals(None, parse_line({}))
        self.assertEquals(None, parse_line((42,)))
        self.assertEquals(None, parse_line(False))
        self.assertEquals(None, parse_line(None))

    def test_parse_line_wrong_format(self):
        self.assertEquals(None, parse_line(''))
        self.assertEquals(None, parse_line('42 foo: killed by bar.'))
        self.assertEquals(None, parse_line('1 42 foo'))
        self.assertEquals(None, parse_line('1 0x2A foo: bar.'))

    def test_parse_line(self):
        self.assertSequenceEqual(('foo', 2, 'text'),
                                 parse_line('1 2 foo: text'))
        self.assertSequenceEqual(('foo:', 45, 'text bar'),
                                 parse_line('12 45 foo:: text bar'))

    # == .get_scores == #

    def test_get_scores_popen_call(self):
        scs = get_scores()
        self.assertSequenceEqual(['rogue', '-s'], FakePopen.last_args)

    def test_get_scores_popen_call_with_custom_command(self):
        cmd = 'xr$A&-%'
        scs = get_scores(cmd)
        self.assertSequenceEqual([cmd, '-s'], FakePopen.last_args)

    def test_get_scores_unknown_command(self):
        subprocess.Popen = self._popen
        scs = get_scores('idontexist-yeah-i-really-dont')
        self.assertSequenceEqual([], scs)

    def test_get_scores(self):
        scs = get_scores()
        self.assertEqual(10, len(scs))
        self.assertEqual(('baptiste', 783, 'killed on level 8 by a centaur.'),
                         scs[0])
        self.assertEqual(('baptiste', 163, 'killed on level 2 by a hobgoblin.'),
                         scs[-1])
