#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

def users_key(group="default"):
    return ndb.Key('users', group)

class User(ndb.Model):
    uid = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_visit = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def _by_uid(cls, uid):
        u = cls.query(User.uid == uid).get()
        if u is not None:
            return u.uid

    #@classmethod
    #def _by_id(cls, uid):
    #    return cls.get_by_id(uid, parent=users_key())

    @classmethod
    def _by_name(cls, name):
        #u = cls.all().filter('name =', name).get()
        u = cls.query(User.name == name).get()
        return u

    @classmethod
    def _register(cls, uid, name, pw, email=None):
        return cls(parent = users_key(), 
                   uid = uid, 
                   name = name,
                   email = email)
