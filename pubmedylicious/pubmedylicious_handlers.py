#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import addlib
import webapp2
import json, ast
import eUtils
import urllib
from basehandler import basehandler
from google.appengine.ext import db
from itertools import chain
from collections import defaultdict
from lib.utils.summarize import *
from lib.utils.absprocess import *
from lib.utils.pdf2text import *
from lib.models.querymodels import *
from google.appengine.ext import blobstore
import config
import logging
from google.appengine.ext.webapp import blobstore_handlers


class Home(basehandler.BaseHandler):

    def get(self):
        if self.uid and self.uname:
            
            #upload_url = blobstore.create_upload_url('/upload')
            self.render('home.html', username = self.uname,
                        uid = self.uid)

        else:
            self.render('home.html')

    def post(self):
        query_terms = self.request.get('query')
        query_terms = query_terms.replace('\n', '').replace(' ', '+').upper()

        # Minimal check for term inconsistencies.
        for forbidden in ['/', ' ', 'CRDT', 'CRDAT']:
            if forbidden in query_terms: raise TermException(forbidden)
            success = False

        #check if the query already exists on DB
        queryexist = False
        querydb = Query._by_query_terms(str(query_terms))
        if querydb:
            queryexist = True

        if not queryexist:
            try:
                abstlst = eUtils.fetch_abstr(
                    term = query_terms,
                    retmax = config.RETMAX,
                    email = config.ADMAIL
                )
            except (eUtils.PubMedException, eUtils.NoHitException):
                # PubMed error or no nit.
                success = False
            else:
                success = True

        if self.uname and queryexist:
            self.redirect('/result/%s' % querydb.key.id())

        elif self.uname and not queryexist and success:
            logging.error('not exist')
            if success:
                (authdict,journaldict,num_abst,abstlst, pubyeardict, countrydict) = absProcess(abstlst)


                q = Query._register(uname=self.uname,
                                    uid = self.uid,
                                    query_terms=query_terms,
                                    authdict = authdict,
                                    journaldict = journaldict,
                                    num_abst = num_abst,
                                    abstlst = abstlst,
                                    pubyeardict = pubyeardict,
                                    #pubyear = pubyear,
                                    #pubvalues= pubvalues,
                                    countrydict = countrydict,
                                    )

                q.put()
                self.redirect('/result/%s' % str(q.key.id()))

        elif not self.uname and not exist and success: 
            (authdict,journaldict,num_abst,abstlst, pubyeardict, countrydict) = absProcess(abstlst)
            self.render('result.html', 
                        query_terms = query_terms,
                        authdict = authdict,
                        journaldict = journaldict, 
                        num_abst = num_abst, 
                        abstlst = abstlst,
                        pubyeardict = pubyeardict,
                        #pubyear= pubyear,
                        #pubvalues= pubvalues,
                        countrydict = countrydict
                        )
        else:
            self.response.write('Failed to fetch Pubmed Abstracts')


class ResultById(basehandler.BaseHandler):
    """
    To get the result given the query_id from the datastor
    """
    def get(self, query_id):
        result = Query._by_id(int(query_id))
        #abstlst = pickle.loads(result.abst)
        #abstlst = result.abst
        #(authdict,journaldict,num_abst,abstlst, pubyeardict, countrydict) = absProcess(abstlst)
        pubyeardict = ast.literal_eval(json.dumps(result.pubyeardict))
        pubyeardict = collections.OrderedDict(sorted(pubyeardict.items()))
        logging.error(pubyeardict)

        self.render('result.html', 
                    query_terms = result.query_terms,
                    authdict = result.authdict,
                    journaldict = result.journaldict, 
                    num_abst = result.num_abst, 
                    abstlst = result.abstlst, 
                    pubyeardict = pubyeardict,
                    #pubyear = pubyear,
                    countrydict = result.countrydict,
                    username = self.uname)

class HistoryQuery(basehandler.BaseHandler):
    def get(self, uid):
        logging.error(self.uid)
        results = Query._by_uid(self.uid)
        if results:
            self.render("history.html", username=self.uname, results=results)
        else:
            self.response.write('something not write with db fetching')

class Summary(basehandler.BaseHandler):

  def post(self):
    """Convert, parse and print text from converted PDF."""
    pdf = self.request.POST['file'].file.read()
    text = pdf2text(pdf)
    text = text.decode('utf-8')
    (summary, fdist_words) = summarize(text)
    #summary = [text.decode('utf-8') for text in summary]
    self.render("summary.html", summary = summary, 
            fdist_words = fdist_words[:10])

