#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

"""
Step 4 : evaluation of the extracted keywords
    (1) convert csv file to a dictionnary
    (2) 3 mesures of evaluation : recall/precision/f-mesure, P@N, MAP (mean average precision)
"""

import csv
import glob
import os

def csv_to_dico(filein):
    """convert csv file to a dictionnary
    filein : csv file that contains 2 columns : 
    col 1 --> document number , col2 --> keywords that assigned to the document
    we keep the original word
    """
    dico = {}
    with open(filein, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        dico = {rows[0]:rows[1] for rows in reader}
    return dico

def csv_to_dico_lemma(filein):
    """convert csv file to a dictionnary
    filein : csv file that contains 2 columns : 
    col 1 --> document number , col2 --> keywords that assigned to the document
    convert in word lemma
    """
    import spacy
    sp = spacy.load("fr_core_news_sm")
    dico = {}
    with open(filein, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        for rows in reader:
            docn = rows[0]
            mcs_lemma = []
            for mc in rows[1].split(','):
                if ' ' in mc:
                    multimc = ' '.join([token.lemma_ for token in sp(mc)])
                    mc_lemma = multimc.replace('’ ', '’')
                else:
                    mc_lemma = ''.join([token.lemma_ for token in sp(mc)])
                mcs_lemma.append(mc_lemma)
                
            mcs_lemma_str = ','.join(mcs_lemma)
            dico[docn] = mcs_lemma_str

    return dico
    
def csv_to_dico_stem(filein):
    """convert csv file to a dictionnary
    filein : csv file that contains 2 columns : 
    col 1 --> document number , col2 --> keywords that assigned to the document
    convert in stemmed words
    """
    from nltk import word_tokenize
    from nltk.stem import SnowballStemmer
    fr = SnowballStemmer('french')
    dico = {}
    with open(filein, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        for rows in reader:
            docn = rows[0]
            mcs_stemmed = []
            for mc in rows[1].split(','):
                if ' ' in mc:
                    multimc = ' '.join([fr.stem(word) for word in word_tokenize(mc)])
                    mc_stemmed = multimc.replace('’ ', '’')
                else:
                    mc_stemmed = fr.stem(mc)
                mcs_stemmed.append(mc_stemmed)
                
            mcs_stemmed_str = ','.join(mcs_stemmed)
            dico[docn] = mcs_stemmed_str
    return dico

# input_dir : directory that cantains csv file(s) to evaluate
# topn : consider top n keywords in the prediction
# reference : csv file that contains keywords reference
def eval_precision_recall_fmesure_stem(input_dir, reference, topn, beta):
    from statistics import mean
    for input_file in glob.glob(os.path.join(input_dir, '*.csv')):
        dico_ref = csv_to_dico_stem(reference)
        dico_pred = csv_to_dico_stem(input_file)
        r_scores = []
        p_scores = []
        f_scores = []
        for k,v in dico_ref.items():
            if k in dico_pred:
                pred = dico_pred[k].split(',')[:topn]
                true = v.split(',')
                vp = set(pred).intersection(set(true))
                # favoriser le rappel par rapport à la precision, beta = 2                
                if len(vp) == 0:
                    recall = precision = fmesure = 0.0
                else:
                    recall = len(vp) / len(true)
                    precision = len(vp) / len(pred)
                    fmesure = ((1+ beta*beta) *recall *precision) / (beta*beta*precision + recall)
            r_scores.append(recall)
            p_scores.append(precision)
            f_scores.append(fmesure)
        print(round(mean(r_scores), 5),'\t', round(mean(p_scores), 5), '\t', round(mean(f_scores), 5), '\t', input_file)

def eval_p_at_n_stem(input_dir, reference, topn):
    from statistics import mean
    dico_ref = csv_to_dico_stem(reference)
    for input_file in glob.glob(os.path.join(input_dir, '*.csv')):
        dico_pred = csv_to_dico_stem(input_file)

        p_at_n_scores = []
        for k,v in dico_ref.items():
            if k in dico_pred:
                pred = dico_pred[k].split(',')[:topn]
                true = v.split(',')
                vp = set(pred).intersection(set(true))
                if len(vp) == 0:
                    p_at_n = 0.0
                else:
                    p_at_n = len(vp) / topn
            p_at_n_scores.append(p_at_n)
        print(round(mean(p_at_n_scores), 5), '\t', input_file)

def eval_map_stem(input_dir, reference, topn):
    from statistics import mean
    dico_ref = csv_to_dico_stem(reference)
    for input_file in glob.glob(os.path.join(input_dir, '*.csv')):
        dico_pred = csv_to_dico_stem(input_file)
        average_precision = []

        for docn,mcs_pred in dico_pred.items():
            mcs_true_list = dico_ref[docn].split(",")
            precision_doc = []
            nb_pertinent = 0.0
            for i, mc_pred in enumerate(mcs_pred.split(",")[:topn]):
                if mc_pred in mcs_true_list:
                    nb_pertinent+=1
                    score = nb_pertinent / float(i+1)
                    precision_doc.append(score)
            if len(precision_doc) != 0:
                average_precision.append(mean(precision_doc))
            else:
                average_precision.append(0.0)

        print(round(mean(average_precision), 5), '\t', input_file)
        
    
if __name__ =="__main__":
    for i in range(1,11):
        eval_precision_recall_fmesure_stem("path/to/file/directory", "csv/file/that/contains/reference/keywords", 10, i)