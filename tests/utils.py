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
from sensu import utils

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg_file_1 = 'tests/config.json'
        self.cfg_file_2 = 'tests/checks.json'
        self.sample_event = open('tests/event.json', 'r').read()
        # remove env var from other tests
        if os.environ.has_key('SENSU_CONFIG_FILES'):
            del os.environ['SENSU_CONFIG_FILES']
    def tearDown(self):
        pass

    def test_config_files_default(self):
        self.assertTrue('/etc/sensu/config.json' in utils.get_config_files())

    def test_config_files_environment_vars(self):
        os.environ['SENSU_CONFIG_FILES'] = '{0}:{1}'.format(self.cfg_file_1,
            self.cfg_file_2)
        cfgs = utils.get_config_files()
        self.assertTrue(self.cfg_file_1 in cfgs)
        self.assertTrue(self.cfg_file_2 in cfgs)

    def test_load_config(self):
        config = utils.load_config(self.cfg_file_1)
        self.assertTrue(config.has_key('rabbitmq'))
        self.assertTrue(config.has_key('redis'))
        self.assertTrue(config.has_key('api'))
        self.assertTrue(config.has_key('dashboard'))
        self.assertTrue(config.has_key('handlers'))

    def test_read_event(self):
        evt = utils.read_event(self.sample_event)
        self.assertTrue(evt.has_key('check'))
        self.assertTrue(evt.has_key('action'))
        self.assertTrue(evt.has_key('occurrences'))

    def test_load_settings(self):
        os.environ['SENSU_CONFIG_FILES'] = '{0}:{1}'.format(self.cfg_file_1,
            self.cfg_file_2)
        config = utils.load_settings()
        self.assertTrue(config.has_key('rabbitmq'))
        self.assertTrue(config.has_key('redis'))
        self.assertTrue(config.has_key('handlers'))
        self.assertTrue(config.has_key('checks'))
