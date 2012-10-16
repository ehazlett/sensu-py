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
import requests
import os
import glob
import urllib
import sys
try:
    import simplejson as json
except ImportError:
    import json

def api_request(host=None, path='', method='get', \
    data=None, params={}):
    """
    Wrapper function for Sensu requests

    :param host: Sensu API host (default: https://nucleo.arcus.io/api/v1)
    :param path: URL to request
    :param method: HTTP method
    :param data: Data for post (ignored for GETs)
    :param params: Dict of key, value query params

    """
    method = method.lower()
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
    }
    methods = {
        'get': requests.get,
        'post': requests.post,
    }
    if path[0] != '/':
        path = '/{0}'.format(path)
    if params:
        path = '?{0}'.format(urllib.urlencode(params))
    url = '{0}{1}'.format(host, path)
    resp = methods[method](url, data=json.dumps(data), headers=headers)
    return resp

def get_config_files():
    configs = []
    if os.environ.has_key('SENSU_CONFIG_FILES'):
        configs = os.environ.get('SENSU_CONFIG_FILES', '').split(':')
    else:
        configs.append('/etc/sensu/config.json')
        [configs.append(x) for x in glob.glob('/etc/sensu/conf.d/*.json')]
    return configs

def load_config(filename=None):
    if not filename: return {}
    return json.loads(open(filename, 'r').read())

def load_settings():
    data = {}
    for cfg in get_config_files():
        data = dict(data.items() + load_config(cfg).items())
    return data

def read_event(data=None):
    event = {}
    # get from stdin if not specified
    if not data:
        # check for env var (testing)
        if os.environ.has_key('SENSU_EVENT'):
            event = json.loads(os.environ.get('SENSU_EVENT'))
        else:
            event = json.loads(sys.stdin.read())
    else:
        event = json.loads(data)
    return event
