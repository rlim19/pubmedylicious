#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Adapted from ptwobrussell 
# https://github.com/ptwobrussell/Mining-the-Social-Web/blob/master/python_code/blogs_and_nlp__summarize.py

import addlib
import nltk
import numpy
from nltk.tokenize import RegexpTokenizer

N = 100  # Number of words to consider
CLUSTER_THRESHOLD = 5  # Distance between words to consider
TOP_SENTENCES = 5  # Number of sentences to return for a "top n" summary

# Approach taken from "The Automatic Creation of Literature Abstracts" by H.P. Luhn
def _score_sentences(sentences, important_words):
    scores = []
    sentence_idx = -1

    for s in [nltk.tokenize.word_tokenize(s) for s in sentences]:

        sentence_idx += 1
        word_idx = []

        # For each word in the word list...
        for w in important_words:
            try:
                # Compute an index for where any important words occur in the sentence
                word_idx.append(s.index(w))
            except ValueError, e: # w not in this particular sentence
                pass

        word_idx.sort()

        # It is possible that some sentences may not contain any important words at all
        if len(word_idx)== 0: continue

        # Using the word index, compute clusters by using a max distance threshold
        # for any two consecutive words

        clusters = []
        cluster = [word_idx[0]]
        i = 1
        while i < len(word_idx):
            if word_idx[i] - word_idx[i - 1] < CLUSTER_THRESHOLD:
                cluster.append(word_idx[i])
            else:
                clusters.append(cluster[:])
                cluster = [word_idx[i]]
            i += 1
        clusters.append(cluster)

        # Score each cluster. The max score for any given cluster is the score
        # for the sentence

        max_cluster_score = 0
        for c in clusters:
            significant_words_in_cluster = len(c)
            total_words_in_cluster = c[-1] - c[0] + 1
            score = 1.0 * significant_words_in_cluster \
                * significant_words_in_cluster / total_words_in_cluster

            if score > max_cluster_score:
                max_cluster_score = score

        scores.append((sentence_idx, score))

    return scores

def summarize(txt):
    sentences = [s for s in nltk.tokenize.sent_tokenize(txt)]
    normalized_sentences = [s.lower() for s in sentences]

    #words = [w.lower() for sentence in normalized_sentences for w in
    #        nltk.tokenize.word_tokenize(sentence)]

    tokenizer = RegexpTokenizer(r'\w+')
    words = [w.lower() for sentence in normalized_sentences for w in
             tokenizer.tokenize(sentence)]

    #proper_nouns = [for sentence in normalized_sentences for w]

    fdist = nltk.FreqDist(words)

    #top_n_words = [w[0] for w in fdist.items()
    #        if w[0] not in nltk.corpus.stopwords.words('english')][:N]

    # fdist_words is a tuple, e.g [('word', 4), ('word2', 2)]
    fdist_words = [w for w in fdist.items()
                   if w[0] not in nltk.corpus.stopwords.words('english')][:N]


    #scored_sentences = _score_sentences(normalized_sentences, top_n_words)
    scored_sentences = _score_sentences(normalized_sentences, fdist_words[0])

    top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-TOP_SENTENCES:]

    # Decorate the post object with summaries
    for idx,score in top_n_scored:
        sentences[idx] = '<b>' + sentences[idx] + '</b>'

    return (sentences, fdist_words)
