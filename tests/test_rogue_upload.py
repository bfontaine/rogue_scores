# -*- coding: UTF-8 -*-

import platform
import subprocess
from httmock import all_requests, response, HTTMock
import requests

if platform.python_version() < '2.7':
    import unittest2 as unittest
else:
    import unittest

from rogue_scores.upload import post_scores

@all_requests
def server_mock_ok(url, req):
    if req.method == 'POST':
        return response(200, bytes('ok'.encode('utf-8')))

@all_requests
def server_mock_not_ok(url, req):
    return u'some {weird\\mess\x03ag*$e'

@all_requests
def server_mock_wrong_format(url, req):
    if req.method == 'POST':
        return u'ok'

@all_requests
def server_mock_http_error(url, req):
    return response(500, 'oops')

@all_requests
def server_mock_connection_error(url, req):
    raise requests.exceptions.ConnectionError()


class TestRogueUpload(unittest.TestCase):

    # == .post_scores == #

    def test_post_scores_ok(self):
        with HTTMock(server_mock_ok):
            r = post_scores([])
        self.assertTrue(r)

    def test_post_scores_unicode_response(self):
        with HTTMock(server_mock_wrong_format):
            r = post_scores([])
        self.assertFalse(r)

    def test_post_scores_wrong_response(self):
        with HTTMock(server_mock_not_ok):
            r = post_scores([])
        self.assertFalse(r)

    def test_post_scores_http_error(self):
        with HTTMock(server_mock_http_error):
            r = post_scores([])
        self.assertFalse(r)

    def test_post_scores_connection_error(self):
        with HTTMock(server_mock_connection_error):
            r = post_scores([])
        self.assertFalse(r)

