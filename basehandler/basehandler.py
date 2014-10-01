#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
import webapp2
import json
import urllib
from lib.models.usermodels import *

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'),
                               autoescape=True)

def render_str(self, template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render_json(self, d):
            json_txt = json.dumps(d)
            self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            self.write(json_txt)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def next_url(self):
        self.request.headers.get('referer', '/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.request.cookies.get('user_id')
        
        self.uid = uid and User._by_uid(uid)
        self.uname = urllib.unquote(self.request.cookies.get('user_name', ''))
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'
