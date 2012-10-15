# Python Sensu Plugin
This is a Python based Sensu (https://github.com/sensu) plugin.

[![Build Status](https://secure.travis-ci.org/ehazlett/sensu-py.png)](http://travis-ci.org/ehazlett/sensu-py)

Currently, only the handler implementation is complete.  It was (almost) directly
ported from https://github.com/sensu/sensu-plugin/blob/master/lib/sensu-handler.rb

The Python plugin will take care of things like check stashes (silencing), dependency check monitoring,
periodic notifications, etc.

# Usage

Create a Sensu handler, derive from `sensu.Handler`, and override the `handle` method.
The Python plugin will handle the filters, checks, etc.


