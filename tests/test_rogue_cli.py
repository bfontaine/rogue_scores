# -*- coding: UTF-8 -*-

import os
import os.path
import sys
import platform
import tempfile

if platform.python_version() < '3.0':
    from StringIO import StringIO
else:
    from io import StringIO

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

import rogue_scores.cli
from rogue_scores.cli import run, set_server

def noop(*args, **kwargs):
    return

class TestRogueCLI(unittest.TestCase):

    def setUp(self):
        self._server = rogue_scores.cli.SERVER_FILE
        self._tmp = tempfile.NamedTemporaryFile(delete=False)
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        self._getscores = rogue_scores.cli.get_scores
        self._postscores = rogue_scores.cli.post_scores
        rogue_scores.cli.get_scores = noop
        rogue_scores.cli.post_scores = noop
        self._exit = sys.exit
        sys.exit = self.mkExit()
        rogue_scores.cli.SERVER_FILE = self._tmp.name
        os.unlink(self._tmp.name)

    def tearDown(self):
        rogue_scores.cli.SERVER_FILE = self._server
        sys.stdin = self._stdin
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        sys.exit = self._exit
        rogue_scores.cli.get_scores = self._getscores
        rogue_scores.cli.post_scores = self._postscores

    def mute(self):
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def mkFakeInput(self, *ret):
        sys.stdin = StringIO('\n'.join(ret)+'\n')
        self.mute()

    def getServer(self):
        self.assertTrue(os.path.isfile(self._tmp.name))
        with open(self._tmp.name) as f:
            return f.read()

    def setScores(self, scs):
        rogue_scores.cli.get_scores = lambda: scs

    def fakePostScores(self, ret):
        self._post_args = None

        def post_scores(*args, **kwargs):
            self._post_args = args
            self._post_kwargs = kwargs
            return ret
        rogue_scores.cli.post_scores = post_scores

    def mkExit(self):
        self._last_exit = None
        def exit(code):
            self._last_exit = code
        return exit

    # == .set_server == #

    def test_set_server_no_input(self):
        self.mkFakeInput('', 'foo')
        set_server()
        self.assertEquals('foo', self.getServer())

    def test_set_server_with_port(self):
        self.mkFakeInput('', 'foobar:4242')
        set_server()
        self.assertEquals('foobar:4242', self.getServer())

    def test_set_server_with_http(self):
        self.mkFakeInput('', 'http://foobar')
        set_server()
        self.assertEquals('foobar', self.getServer())

    def test_set_server_with_https(self):
        self.mkFakeInput('', 'https://fooq')
        set_server()
        self.assertEquals('fooq', self.getServer())

    def test_set_server(self):
        self.mkFakeInput('', 'x')
        set_server()
        self.assertEquals('x', self.getServer())


    # == .run == #

    def test_cli_run_no_server_no_scores_abort(self):
        srv = 'awsz'
        self.mkFakeInput(srv)
        self.setScores([])
        self.fakePostScores(False)
        run()
        self.assertEquals(srv, self.getServer())
        self.assertEquals(1, self._last_exit)
        self.assertEquals(None, self._post_args)

    def test_cli_run_no_server_post_error(self):
        srv = 'qzsao'
        scs = [('user', 42, 'foo')]
        self.mkFakeInput(srv)
        self.setScores(scs)
        self.fakePostScores(False)
        run()
        self.assertEquals(srv, self.getServer())
        self.assertEquals(2, self._last_exit)
        self.assertSequenceEqual([scs], self._post_args)
        self.assertEquals({'target':srv}, self._post_kwargs)

    def test_cli_run_no_server(self):
        srv = 'qqq'
        scs = [('user', 42, 'foo')]
        self.mkFakeInput(srv)
        self.setScores(scs)
        self.fakePostScores(True)
        run()
        self.assertEquals(srv, self.getServer())
        self.assertEquals(None, self._last_exit)
        self.assertSequenceEqual([scs], self._post_args)
        self.assertEquals({'target':srv}, self._post_kwargs)

    def test_cli_run_env_server(self):
        self.mute()
        srv = 'qqq'
        scs = [('user', 42, 'foo')]
        rogue_scores.cli.os.environ['ROGUE_SCORES_SERVER'] = srv
        self.setScores(scs)
        self.fakePostScores(True)
        run()
        self.assertEquals(srv, self.getServer())
        self.assertEquals(None, self._last_exit)
        self.assertSequenceEqual([scs], self._post_args)
        self.assertEquals({'target':srv}, self._post_kwargs)
        del rogue_scores.cli.os.environ['ROGUE_SCORES_SERVER']
