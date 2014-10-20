#! /usr/bin/env python
# -*- coding: utf-8 -*-
from hashlib import sha1
import datetime
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
from lib.models.papermodels import *
from google.appengine.ext import blobstore
import config
import logging
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.runtime import DeadlineExceededError

urlfetch.set_default_fetch_deadline(60)

#class Test(basehandler.BaseHandler):
#    def get(self):
#        self.render('sharelink.html')

def abst_key(name="default"):
    return ndb.Key('abst', name)  

class Abst(ndb.Model):
    abstlst = ndb.JsonProperty(indexed=False)
    @classmethod
    def _register(cls, abstlst):
        return cls(parent = abst_key(), 
                   abstlst = abstlst,
                   )
    @classmethod
    def _by_query_terms(cls, query_terms):
        q = cls.query(Query.query_terms == query_terms).get()
        return q

class PubmedHandler(basehandler.BaseHandler):
    def get(self):
        abstlst = Abst.query()
        self.render('pubmed.html', abstlst = abstlst)
    def post(self):
        query_terms = self.request.get('query')
        query_terms = query_terms.replace('\n', '').replace(' ', '+').upper()
        taskqueue.add(url='/dev/worker', params={'query': query_terms})
        self.redirect('/dev')


class PubmedWorker(basehandler.BaseHandler):
    def post(self):
        query = self.request.get('query')
        query = query.replace('\n', '').replace(' ', '+').upper()
        
        @ndb.transactional
        def update_abst():
            abstlst = eUtils.fetch_abstr(
                        term = query,
                        retmax = config.RETMAX,
                        email = config.ADMAIL
                        )
            # abst (summarized) 
            #for abst in abstlst:
            #    (summary, fdist) = summarize(abst['text'])
            #    summary = ' '.join(summary)
            #    abst['text'] = summary
            a = Abst._register(abstlst = abstlst)
            a.put()

        update_abst()

class Home(basehandler.BaseHandler):

    def get(self):
        if self.uid and self.uname:
            
            upload_url = blobstore.create_upload_url('/upload')
            self.render('home.html', username = self.uname,
                        uid = self.uid, upload_url = upload_url)
        else:
            self.render('home.html')

    def post(self):
        try:
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

            # login user and non-login user
            if self.uid:
                if queryexist:
                    self.redirect('/result/%s' % querydb.key.id())
                elif not queryexist and success:
                    (authdict,journaldict,num_abst,abstlst, pubyeardict, countrydict) = absProcess(abstlst)
                    q = Query._register(uname=self.uname,
                                        uid = self.uid,
                                        query_terms=query_terms,
                                        authdict = authdict,
                                        journaldict = journaldict,
                                        num_abst = num_abst,
                                        abstlst = abstlst,
                                        pubyeardict = pubyeardict,
                                        countrydict = countrydict,
                                        )

                    q.put()
                    self.redirect('/result/%s' % str(q.key.id()))

            elif not self.uid: 
                if queryexist:
                    result = Query._by_id(int(querydb.key.id()))
                    pubyeardict = ast.literal_eval(json.dumps(result.pubyeardict))
                    pubyeardict = collections.OrderedDict(sorted(pubyeardict.items()))
                    query_terms = result.query_terms
                    authdict = result.authdict
                    journaldict = result.journaldict 
                    num_abst = result.num_abst 
                    abstlst = result.abstlst 
                    pubyeardict = pubyeardict
                    countrydict = result.countrydict
                    

                elif not queryexist and success:
                    logging.error('here is the error')
                    (authdict,journaldict,num_abst,abstlst, pubyeardict, countrydict) = absProcess(abstlst)
                    pubyeardict = ast.literal_eval(json.dumps(pubyeardict))
                    pubyeardict = collections.OrderedDict(sorted(pubyeardict.items()))

                self.render('result.html', 
                            query_terms = query_terms,
                            authdict = authdict,
                            journaldict = journaldict, 
                            num_abst = num_abst, 
                            abstlst = abstlst,
                            pubyeardict = pubyeardict,
                            countrydict = countrydict,
                            )
            else:
                self.response.write('Failed to fetch Pubmed Abstracts')

        except DeadlineExceededError:
            self.response.write('Deadline Exceeded!')

class About(basehandler.BaseHandler):
    def get(self):
        self.render('about.html')

class ResultById(basehandler.BaseHandler):
    """
    To get the result given the query_id from the datastor
    Only for the logged-in users
    """
    def get(self, query_id):
        result = Query._by_id(int(query_id))
        pubyeardict = ast.literal_eval(json.dumps(result.pubyeardict))
        pubyeardict = collections.OrderedDict(sorted(pubyeardict.items()))
        username = ''
        if self.uid:
            username = self.uname
        self.render('result.html', 
                    query_terms = result.query_terms,
                    authdict = result.authdict,
                    journaldict = result.journaldict, 
                    num_abst = result.num_abst, 
                    abstlst = result.abstlst, 
                    pubyeardict = pubyeardict,
                    #pubyear = pubyear,
                    countrydict = result.countrydict,
                    username = username,
                    uid = self.uid)

class HistoryQuery(basehandler.BaseHandler):
    def get(self, uid):
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

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler,
                    basehandler.BaseHandler):
    """
    handle the file post
    """
    def post(self):
        if self.uid:
            # NB: 'get_uploads' is a list of 'BlobInfo' objects.
            blob_info = self.get_uploads('file')[0]
            # Set the SHA1 digest of the file as key name.
            # This is unique, not ridiculously long and contains
            # only URL characters.
            sha1_digest = sha1(blob_info.filename).hexdigest()
            download_link = 'http://pubmedylicious.appspot.com/download/%s'%(sha1_digest) 
            logging.error(download_link)
            paper_ref = PaperRef(
                id = sha1_digest,
                uid = self.uid,
                uname = self.uname,
                download_link = download_link, 
                blob_key = blob_info.key(),
            )
            paper_ref.put()

            self.render("sharelink.html", paper_link=sha1_digest)


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, file_id):
        paper_info = PaperRef.get_by_id(file_id)
        self.send_blob(blobstore.BlobInfo.get(paper_info.blob_key),
                       save_as = True)


class ByBlobKeyHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, path):
        blob_info = blobstore.BlobInfo.get(path)
        self.send_blob(blob_info, save_as=True)


class DeleteHandler(blobstore_handlers.BlobstoreDownloadHandler):
   def get(self):
      thirty_days_ago = datetime.datetime.today() \
                       + datetime.timedelta(days=-30)
      blob_count = blobstore.BlobInfo.all().count()
      all_blobs_query = blobstore.BlobInfo.all().fetch(blob_count)
      for blob in all_blobs_query:
         if blob.creation < thirty_days_ago:
            blob.delete()
      all_BlobRef_query = PaperRef.all().fetch(blob_count)
      for blob_ref in all_BlobRef_query:
         if blob_ref.creation_time < thirty_days_ago:
            blob_ref.delete()
