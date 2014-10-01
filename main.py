#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

from webapp2_extras import routes
from pubmedylicious import pubmedylicious_handlers
from userAccount import user_handlers

DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

id_re = r'(/(?:[a-zA-Z0-9]+/?)*)'
ROUTES = [webapp2.Route(r'/login/<:.*>', user_handlers.Login, handler_method='any'),
          webapp2.Route('/logout', user_handlers.Logout),
          webapp2.Route('/', pubmedylicious_handlers.Home),
          webapp2.Route('/result/<:.*>', pubmedylicious_handlers.ResultById),
          webapp2.Route('/history/<:.*>', pubmedylicious_handlers.HistoryQuery),
          webapp2.Route('/summary', pubmedylicious_handlers.Summary),
          ]

app = webapp2.WSGIApplication(ROUTES, debug=True)

