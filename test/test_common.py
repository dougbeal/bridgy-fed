# coding=utf-8
"""Unit tests for common.py."""
from __future__ import unicode_literals
import json
import logging

import mock
from oauth_dropins.webutil import util
from oauth_dropins.webutil.testutil import requests_response
import requests
from webob import exc

import common
import testutil

HTML = requests_response('<html></html>', headers={
    'Content-Type': common.CONTENT_TYPE_HTML,
})
HTML_WITH_AS2 = requests_response("""\
<html><meta>
<link href='http://as2' rel='alternate' type='application/activity+json'>
</meta></html>
""", headers={
    'Content-Type': common.CONTENT_TYPE_HTML,
})
AS2_OBJ = {'foo': ['bar']}
AS2 = requests_response(AS2_OBJ, headers={
    'Content-Type': common.CONTENT_TYPE_AS2,
})
NOT_ACCEPTABLE = requests_response(status=406)


class CommonTest(testutil.TestCase):

    @mock.patch('requests.get', return_value=AS2)
    def test_get_as2_direct(self, mock_get):
        resp = common.get_as2('http://orig')
        self.assertEqual(AS2, resp)
        mock_get.assert_has_calls((
            self.req('http://orig', headers=common.CONNEG_HEADERS_AS2_HTML),
        ))

    @mock.patch('requests.get', side_effect=[HTML_WITH_AS2, AS2])
    def test_get_as2_via_html(self, mock_get):
        resp = common.get_as2('http://orig')
        self.assertEqual(AS2, resp)
        mock_get.assert_has_calls((
            self.req('http://orig', headers=common.CONNEG_HEADERS_AS2_HTML),
            self.req('http://as2', headers=common.CONNEG_HEADERS_AS2),
        ))

    @mock.patch('requests.get', return_value=HTML)
    def test_get_as2_only_html(self, mock_get):
        with self.assertRaises(exc.HTTPBadGateway):
            resp = common.get_as2('http://orig')

    @mock.patch('requests.get', return_value=NOT_ACCEPTABLE)
    def test_get_as2_not_acceptable(self, mock_get):
        with self.assertRaises(exc.HTTPBadGateway):
            resp = common.get_as2('http://orig')
