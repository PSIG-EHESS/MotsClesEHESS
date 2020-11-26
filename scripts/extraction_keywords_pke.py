#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

"""
Step 3 : extract keywords from contents of articles

source :  https://boudinfl.github.io/pke/build/html/index.html
"""

import pke
from nltk.corpus import stopwords
from spacy.lang.fr.stop_words import STOP_WORDS
import pandas as pd
from langdetect import detect
import re
from pke import compute_document_frequency
import glob
import os
import csv
import string
import time


# liste des mots vides
stoplist = list(string.punctuation) + list("‘’«»–…❖")
stoplist = stoplist + stopwords.words('french') # nltk
stoplist = list(STOP_WORDS.union(stoplist)) # spacy

# https://spacy.io/models/fr --> label scheme
pos = {'NOUN', 'PROPN', 'ADJ'}

def df_counts(normalization, ngrams, revue):
    # Computing DF counts
    # https://boudinfl.github.io/pke/build/html/tutorials/df.html#computing-df-counts
    # https://github.com/boudinfl/pke/blob/master/examples/compute-df-counts.py
    # compute df counts and store as n-stem -> weight values
    import sys
    from string import punctuation
    from pke import compute_document_frequency

    # path to the collection of documents
    input_dir = 'input/path/'+revue+'/'

    output_file = 'path/to/document_frequency/'+revue+'_'+normalization+'_'+str(ngrams)+'grams.tsv.gz'

    # compute idf weights
    compute_document_frequency(input_dir=input_dir,
                            output_file=output_file,
                            extension='txt', # input file extension
                            language='fr', # language of the input files
                            normalization=normalization, # use porter stemmer. normalization=None, 'lemmatization', 'stemming'
                            stoplist=stoplist,  # stoplist
                            delimiter='\t',  # tab separated output
                            n=ngrams)  # compute n-grams

def compute_lda_model(normalizationmethod, n_topics, revue):
    import logging
    import sys
    from pke import compute_lda_model

    # setting info in terminal
    logging.basicConfig(level=logging.INFO)

    # path to the collection of documents
    input_dir = 'input/dir/'+revue+'/'

    # path to the df weights dictionary, saved as a gzipped csv file
    # output_file = './pke/unsupervised/lda_model/lhomme_'+normalizationmethod+'_'+str(n_topics)+'topics.pickle.gz'
    output_file = './pke/unsupervised/lda_model/'+revue+'_'+normalizationmethod+'_'+str(n_topics)+'topics.pickle.gz'

    # compute idf weights
    compute_lda_model(input_dir=input_dir,
                    output_file=output_file,
                    n_topics=n_topics, # number of topics for the LDA model
                    extension="txt",
                    language="fr",
                    normalization=None)

# Unsupervised models
## Statistical
def test_kpminer(normalizationmethod, document_frequency_file, topn, revue, inputtxtdirectory, lasf, algonumber):
    with open('./pke/'+algonumber+'_kpminer_'+revue+'_'+normalizationmethod+'_top'+str(topn)+'_lasf'+str(lasf)+'_cutof400_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            # 1. create a KPMiner extractor.
            extractor = pke.unsupervised.KPMiner()
            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    encoding='utf-8',
                                    normalization=normalizationmethod)
                
            # 3. select {1-5}-grams that do not contain punctuation marks or
            #    stopwords as keyphrase candidates. Set the least allowable seen
            #    frequency to 5 and the number of words after which candidates are
            #    filtered out to 200.
            extractor.candidate_selection(lasf=lasf, cutoff=400, stoplist=stoplist)

            # 4. weight the candidates using KPMiner weighting function.
            df = pke.load_document_frequency_file(input_file=document_frequency_file)
            extractor.candidate_weighting(df=df, alpha=2.3, sigma=3.0)

            # 5. get the 10-highest scored candidates as keyphrases
            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_tfidf(normalizationmethod,document_frequency_file, ngrams, topn, revue, inputtxtdirectory, algonumber):
    with open('./pke/'+algonumber+'_tfidf_'+revue+'_'+normalizationmethod+'_'+str(ngrams)+'grams_top'+str(topn)+'_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.TfIdf()
            extractor.load_document(input=input_file,
                            language='fr',
                            normalization=None)
            
            # n : the maximun length of the n-grams as candidates
            extractor.candidate_selection(n=ngrams, stoplist=stoplist)

            df = pke.load_document_frequency_file(input_file=document_frequency_file)
            extractor.candidate_weighting(df=df)

            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_yake(normalizationmethod, ngrams, topn, revue, inputtxtdirectory, window, algonumber):
    with open('./pke/'+algonumber+'_yake_'+revue+'_'+normalizationmethod+'_'+str(ngrams)+'grams_top'+str(topn)+'_win'+str(window)+'_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
        
            # 1. create a YAKE extractor.
            extractor = pke.unsupervised.YAKE()

            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=None)

            # 3. select {1-3}-grams not containing punctuation marks and not
            #    beginning/ending with a stopword as candidates.
            extractor.candidate_selection(n=ngrams, stoplist=stoplist)

            # 4. use_stems - whether to use stems instead of lowercase words for weighting, defaults to False.
            extractor.candidate_weighting(window=window,
                                        stoplist=stoplist,
                                        use_stems=True)# None / stemming -- False, None / lemmatisation  --True
            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])

            print(input_file)

## Graph based
def test_textRank(normalizationmethod, topn, revue, inputtxtdirectory,window, algonumber):
    with open('./pke/'+algonumber+'_textRank_'+revue+'_'+normalizationmethod+'_'+str(window)+'window_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.TextRank()
            extractor.load_document(input=input_file, 
                                language='fr', 
                                normalize=None)

            # 3. build the graph representation of the document and rank the words.
            #    Keyphrase candidates are composed from the 33-percent
            #    highest-ranked words.
            extractor.candidate_selection(pos=pos)
            extractor.candidate_weighting(window=window,
                                          pos=pos)

            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_singleRank(normalizationmethod, topn, revue, inputtxtdirectory, window, algonumber):
    with open('./pke/'+algonumber+'_singleRank_'+revue+'_top'+str(topn)+'_'+normalizationmethod+'_'+str(window)+'window_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])    
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.SingleRank()
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=None)

            # 3. select the longest sequences of nouns and adjectives as candidates.
            extractor.candidate_selection(pos=pos)
            extractor.candidate_weighting(window=window,
                                        pos=pos)
            # 4. weight the candidates using the sum of their word's scores that are
            #    computed using random walk. In the graph, nodes are words of
            #    certain part-of-speech (nouns and adjectives) that are connected if
            #    they occur in a window of 10 words.
            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_topicRank(normalizationmethod, topn, revue, inputtxtdirectory, algonumber):
    with open('./pke/'+algonumber+'_topicRank_'+revue+'_top'+str(topn)+'_'+normalizationmethod+'_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.TopicRank()

            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=None)

            # 3. select the longest sequences of nouns and adjectives, that do
            #    not contain punctuation marks or stopwords as candidates.
            extractor.candidate_selection(pos=pos, stoplist=stoplist)

            # 4. build topics by grouping candidates with HAC (average linkage,
            #    threshold of 1/4 of shared stems). Weight the topics using random
            #    walk, and select the first occuring candidate from each topic.
            extractor.candidate_weighting(threshold=0.74, method='average')
            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_multipartiteRank(normalizationmethod,topn, revue, inputtxtdirectory, algonumber):
    with open('./pke/'+algonumber+'_multipartiteRank_'+revue+'_top'+str(topn)+'_'+normalizationmethod+'_txtv2.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            
            extractor = pke.unsupervised.MultipartiteRank()

            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=normalizationmethod)

            # 3. select the longest sequences of nouns and adjectives, that do
            #    not contain punctuation marks or stopwords as candidates.
            extractor.candidate_selection(pos=pos, stoplist=stoplist)

            extractor.candidate_weighting(alpha=1.1,
                              threshold=0.74,
                              method='average')

            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_topicalPageRank(normalizationmethod, pathldamodel, topn, revue, inputtxtdirectory, algonumber):
    with open('./pke/'+algonumber+'_topicalPageRank_'+revue+'_top'+str(topn)+'_'+normalizationmethod+'.csv', 'w', encoding='utf-8') as outcsv:
    # with open('./pke/topicalPageRank_lhomme_top'+str(topn)+'_'+normalizationmethod+'.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        
        # define the valid Part-of-Speeches to occur in the graph
        postag = {'NOUN', 'PROPN', 'ADJ', 'ADP'}
        # define the grammar for selecting the keyphrase candidates
        # v1 : le meuilleur
        # grammar = "NP: {<NOUN|ADJ><ADP>*<ADJ|NOUN>*}"
        # v2 grammar = "NP: {<NOUN|ADJ|PROPN><ADP|PROPN>*<ADJ|NOUN>*}"
        # v3 grammar = "NP: {<NOUN|ADJ|PROPN>+<ADP|PROPN>*<ADJ|NOUN>*}" 
        # version4
        grammar = 'NP:{<NOUN|ADJ|PROPN><NOUN|ADJ|PROPN|ADP>*<NOUN>*}'
        # version5 : grammar = 'NP:{<NOUN><ADJ>*}'
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.TopicalPageRank()
            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=None)

            extractor.candidate_selection(grammar=grammar)

            extractor.candidate_weighting(window=10,
                                        pos=postag,
                                        lda_model=pathldamodel,
                                        stoplist=stoplist)

            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

def test_positionRank(normalizationmethod, topn, revue, inputtxtdirectory, algonumber):
    with open('./pke/'+algonumber+'_positionRank_'+revue+'_top'+str(topn)+'_'+normalizationmethod+'.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_prediction'])
        
        # define the valid Part-of-Speeches to occur in the graph
        postag = {'NOUN', 'PROPN', 'ADJ', 'ADP'}
        # define the grammar for selecting the keyphrase candidates
        # v1 grammar = "NP: {<NOUN|ADJ><ADP>*<ADJ|NOUN>*}"
        # v2 grammar = "NP: {<NOUN|ADJ|PROPN><ADP|PROPN>*<ADJ|NOUN>*}"
        # v3 grammar = "NP: {<NOUN|ADJ|PROPN>+<ADP|PROPN>*<ADJ|NOUN>*}"
        # v4 
        grammar = 'NP:{<NOUN|ADJ|PROPN><NOUN|ADJ|PROPN|ADP>*<NOUN>*}'
        for input_file in glob.glob(os.path.join(inputtxtdirectory, '*.txt')):
            extractor = pke.unsupervised.PositionRank()
            # 2. load the content of the document.
            extractor.load_document(input=input_file,
                                    language='fr',
                                    normalization=normalizationmethod)

            extractor.candidate_selection(grammar=grammar,
                              maximum_word_number=5)

            extractor.candidate_weighting(window=10,
                                        pos=postag)

            doc_n = re.search(r'NTSRC_(\d+)', input_file).group(1)
            topnmc = [keyphrase for keyphrase, score in extractor.get_n_best(n=topn)]
            topnmc = ','.join(topnmc)
            writer.writerow([str(doc_n),topnmc])
            print(input_file)

if __name__ == '__main__':
    test_yake_txt('stemming',2, 10, 'etudesrurales', 'path/to/directory/of/the/journal', 2,'algonumber')