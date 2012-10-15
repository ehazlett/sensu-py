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
import os
import sys
import utils
try:
    import simplejson as json
except ImportError:
    import json

class HandlerException(BaseException):
    pass

class Handler(object):
    def __init__(self):
        self.settings = utils.load_settings()
        self.event = {}
        self.read_event()
        if not os.environ.has_key('SENSU_TEST'):
            self.filter()
            self.handle()

    def _api_request(self, path='', method='get', \
        data=None, params={}):
        api_url = 'http://{0}:{1}'.format(self.settings.get('api', {}).get('host'),
            self.settings.get('api', {}).get('port'))
        return utils.api_request(host=api_url, path=path, method=method,
            data=data, params=params)

    def bail(self, msg):
        print('{0}: {1}'.format(msg,
            self.event.get('client', {}).get('name')))
        # env var for testing
        if not os.environ.has_key('SENSU_TEST'):
            sys.exit(0)

    def read_event(self):
        self.event = utils.read_event()

    def handle(self):
        raise HandlerException('No handle functionality defined')

    def filter(self):
        self.filter_disabled()
        self.filter_repeated()
        self.filter_silenced()
        self.filter_dependencies()

    def filter_disabled(self):
        if self.event.get('check', {}).get('alert') == False:
            self.bail('alert disabled')
            return True
        return False

    def filter_repeated(self):
        chk = self.event.get('check', {})
        occurrences = chk.get('occurrences', 1)
        interval = chk.get('interval', 30)
        refresh = chk.get('refresh', 1800)
        if self.event.get('occurrences') < occurrences:
            self.bail('not enough occurrences')
        if self.event.get('occurrences') > occurrences and \
            self.event.get('action') == 'create':
            number = int(float(refresh) / float(interval))
            if self.event.get('occurrences') % number != 0:
                self.bail('only handling every {0} occurrences'.format(
                    number))
                return True
        return False

    def stash_exists(self, path):
        r = self._api_request('/stash' + path)
        return r.status_code == 200

    def filter_silenced(self):
        client_name = self.event.get('client', {}).get('name')
        check_name = self.event.get('check', {}).get('name')
        stashes = {
            'client': '/silence/{0}'.format(client_name),
            'check': '/silence/{0}/{1}'.format(client_name, check_name),
        }
        for s in stashes:
            if self.stash_exists(s):
                self.bail('{0} alerts silenced'.format(s))
                return True
        return False

    def event_exists(self, client, check):
        r = self._api_request('/event/{0}/{1}'.format(client, check))
        return r.status_code == 200

    def filter_dependencies(self):
        check = self.event.get('check', {})
        if check.has_key('dependencies'):
            dependencies = check.get('dependencies', [])
            if isinstance(dependencies, list):
                for d in dependencies:
                    if self.event_exists(self.event.get('client'), d):
                        self.bail('check dependency event exists')
                        return True
        return False
