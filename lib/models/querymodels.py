#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
#import pickle

def query_key(name="default"):
    #return ndb.Key.from_path('query', name)
    return ndb.Key('queries', name)

class Query(ndb.Model):
    username = ndb.StringProperty(required=True)
    uid = ndb.StringProperty(required=True)
    query_terms = ndb.StringProperty(required=True)
    authdict = ndb.JsonProperty(required=True)
    journaldict = ndb.JsonProperty(required=True)
    num_abst = ndb.IntegerProperty(required=True)
    abstlst = ndb.JsonProperty(required=True)
    pubyeardict = ndb.JsonProperty(required=True)
    #pubyear = ndb.JsonProperty(required=True)
    #pubvalues = ndb.JsonProperty(required=True)
    countrydict = ndb.JsonProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def _by_id(cls, page_id):
        return cls.get_by_id(page_id, query_key()) 

    @classmethod
    def _by_uid(cls, uid):
        q = cls.query(Query.uid == uid)
        return q

    @classmethod
    def _by_query_terms(cls, query_terms):
        q = cls.query(Query.query_terms == query_terms).get()
        return q

    @classmethod
    def _register(cls, uname, uid, query_terms, authdict, journaldict, num_abst, abstlst, pubyeardict, countrydict):
        return cls(parent = query_key(), 
                   username = uname,
                   uid = uid,
                   query_terms=query_terms,
                   authdict = authdict,
                   journaldict = journaldict,
                   num_abst = num_abst,
                   abstlst = abstlst,
                   pubyeardict = pubyeardict,
                   #pubyear= pubyear,
                   #pubvalues = pubvalues,
                   countrydict = countrydict,
                   )
