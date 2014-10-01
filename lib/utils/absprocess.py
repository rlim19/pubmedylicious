#! /usr/bin/env python
# -*- coding: utf-8 -*-

import addlib
from lib.utils.summarize import *
from itertools import chain
from collections import defaultdict
import collections
import operator
import re

def absProcess(abstlst):
    """
    Process the list of abstracts in json formats
    > (authdict, journaldict, num_abst, abstlst, pubyeardict, countrydict) = absProcessing(abstlst) 
    """

    num_abst = len(abstlst)

    # pubyear
    #pubdates = [abst['pubdate'] for abst in abstlst]
    #pubdates = filter(None, pubdates)
    #pubyears = [str(re.search(r'(?:\d{4}$)', pubdate).group()) for pubdate in pubdates]
    pubyears = [abst['year'] for abst in abstlst ]
    pubyears = filter(None, pubyears)
    dict_pubtrend = defaultdict(int)
    for pubyear in pubyears:
        dict_pubtrend[pubyear] += 1
    pubyeardict = dict(dict_pubtrend)


    # country
    country_lst = [abst['country'].lower() for abst in abstlst]
    country_lst = filter(None, country_lst)
    dict_country = defaultdict(int)
    for country in country_lst:
        dict_country[country] += 1
    countrydict = dict(dict_country)

    # get only the first 5 fill with color for js (Polar Area Chart)
    # return the e.g dict: {'china': (3, '#F7464A', '#FF5A5E')}
    # value[0] is the freq, value[1] is the color, value[2] is the highlight color
    countrydict= dict(sorted(countrydict.iteritems(),
                      key=operator.itemgetter(1), reverse=True)[:5])
    color = ["#F7464A", "#46BFBD", "#FDB45C", "#949FB1", "#4D5360"]
    highlight = ["#FF5A5E", "#5AD3D1", "FFC870", "#A8B3C5", "#616774"]
    i = 0
    for key, value in countrydict.iteritems():
        countrydict[key] = (value, color[i], highlight[i])
        i += 1

    # author cloud
    author_lst = [abst['author_list'] for abst in abstlst]
    authors = list(chain(*author_lst))
    authors = [author.lower() for author in authors]
    dict_author = defaultdict(int)
    for author in authors:
        dict_author[author] += 1
    authdict = dict(dict_author)                                     
    authdict = dict(sorted(authdict.iteritems(),
                      key=operator.itemgetter(1), reverse=True)[:50])

    # Journal
    journal_lst = [abst['journal'].lower() for abst in abstlst]
    journal_lst = filter(None, journal_lst)
    dict_journal = defaultdict(int)
    for journal in journal_lst:
        dict_journal[journal] += 1
    journaldict = dict(dict_journal)
    journaldict= dict(sorted(journaldict.iteritems(),
                      key=operator.itemgetter(1), reverse=True)[:10])

    # abst (summarized) 
    for abst in abstlst:
        (summary, fdist) = summarize(abst['text'])
        summary = ' '.join(summary)
        abst['text'] = summary


    return (authdict, journaldict, num_abst, abstlst, pubyeardict, countrydict) 
