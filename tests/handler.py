#!/usr/bin/env python
# Copyright (c) 2012 Evan Hazlett
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions
# of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import unittest
import os
from sensu import Handler, HandlerException, utils
from mock import Mock, patch, sentinel
try:
    import simplejson as json
except ImportError:
    import json

class HandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_file_1 = 'tests/config.json'
        self.cfg_file_2 = 'tests/checks.json'
        self.sample_event_file = 'tests/event.json'
        os.environ['SENSU_CONFIG_FILES'] = '{0}:{1}'.format(self.cfg_file_1,
            self.cfg_file_2)
        self.evt_json = open(self.sample_event_file, 'r').read()
        os.environ['SENSU_EVENT'] = self.evt_json
        os.environ['SENSU_TEST'] = 'True'
        self.handler = Handler()

    def tearDown(self):
        pass

    def test_handler_settings(self):
        self.assertTrue(self.handler.settings.has_key('api'))
        self.assertTrue(self.handler.settings.has_key('handlers'))
        self.assertTrue(self.handler.settings.has_key('checks'))

    def test_handler_event(self):
        self.assertNotEqual(self.handler.event, None)
        self.assertTrue(self.handler.event.has_key('check'))
        self.assertTrue(self.handler.event.has_key('action'))

    def test_handle(self):
        with self.assertRaises(HandlerException):
            self.handler.handle()

    def test_filter_disabled(self):
        self.assertEqual(self.handler.filter_disabled(), False)
        self.handler.event['check']['alert'] = False
        self.assertEqual(self.handler.filter_disabled(), True)

    def test_filter_repeated(self):
        self.handler.event['occurrences'] = 2
        self.assertEqual(self.handler.filter_repeated(), True)
        self.handler.event['occurrences'] = 60
        self.assertEqual(self.handler.filter_repeated(), False)

    def test_stash_exists(self):
        handler = Handler()
        with patch.object(Handler, '_api_request') as mock_method:
            sentinel.Response.status_code = 200
            mock_method.return_value = sentinel.Response
            self.assertEqual(handler.stash_exists('/foo'), True)
            sentinel.Response.status_code = 404
            self.assertEqual(handler.stash_exists('/foo'), False)

    def test_filter_silenced(self):
        handler = Handler()
        with patch.object(Handler, '_api_request') as mock_method:
            sentinel.Response.status_code = 200
            mock_method.return_value = sentinel.Response
            self.assertEqual(handler.filter_silenced(), True)
            sentinel.Response.status_code = 404
            self.assertEqual(handler.filter_silenced(), False)

    def test_event_exists(self):
        handler = Handler()
        with patch.object(Handler, '_api_request') as mock_method:
            # check hit
            sentinel.Response.status_code = 200
            mock_method.return_value = sentinel.Response
            self.assertEqual(handler.event_exists('sensu.test', 'cron'), True)
            mock_method.assert_called_with('/event/sensu.test/cron')
            # check miss
            sentinel.Response.status_code = 404
            self.assertEqual(handler.event_exists('sensu.test', 'cron'), False)
            mock_method.assert_called_with('/event/sensu.test/cron')

    def test_filter_dependencies(self):
        handler = Handler()
        with patch.object(Handler, '_api_request') as mock_method:
            # check hit
            sentinel.Response.status_code = 200
            handler.event['check']['dependencies'] = ['foo', 'bar']
            mock_method.return_value = sentinel.Response
            self.assertEqual(handler.filter_dependencies(), True)
            # check miss
            sentinel.Response.status_code = 404
            del handler.event['check']['dependencies']
            self.assertEqual(handler.filter_dependencies(), False)
