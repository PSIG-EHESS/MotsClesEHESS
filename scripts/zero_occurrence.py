#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

import csv
import os

"""
chercher dans les mots clés existants ceux qui n'apparissent pas dans l'article 
--> on les appele "zero occurrences" / "mots-clés absents"

input : csv file that contains document numbers and keywords assigned to each document
output exemple in ../data_additional/zero_occurrence_exemple
"""

def csv_to_dico(filein):
    # convert keywords csv file to dictionary, keep orignal formes
    dico = {}
    with open(filein, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        dico = {rows[0]:rows[1] for rows in reader}
    return dico

def csv_to_dico_lemma(filein):
    # convert keywords csv file to dictionary, use lemma formes
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
    # convert keywords csv file to dictionary, use stem formes
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

def search_zero_occ(dico, revue):
    # STEP 1 : strict matching
    for docn, mcs in dico.items():
        mcl = mcs.strip().split(',')
        with open('../pke/'+revue+'/'+revue+'_TRC_'+str(docn)+'.txt', 'r', encoding='utf-8') as infile:
            texte = infile.read().lower().replace('\n', '')
            for mc in mcl:
                if mc not in texte:
                    print(docn, '\t', mc)

def dico_mono_lemm_stem(filein):
    # STEP 2 : si la forme racinée ou lemmatisée du mono existe dans le texte, on enlève ce mono des zero-occurrences
    # mono : mot-clé simple
    from nltk import word_tokenize
    from nltk.stem import SnowballStemmer
    fr = SnowballStemmer('french')
    import spacy
    sp = spacy.load("fr_core_news_sm")
    
    with open(filein, 'r') as infile:
        dico_mono_traited = {}
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        for rows in reader:
            docn = rows[0]
            with open('../pke/'+revue+'/'+revue+'_NTSRC_'+str(docn)+'.txt', 'r', encoding='utf-8') as txtfile:
                texte = txtfile.read().lower().replace('\n', '')
                mono_multi_zero = []
                for mc in rows[1].split(','):
                    if ' ' not in mc:
                        # mono
                        lemma = ''.join([token.lemma_ for token in sp(mc)])
                        stem = fr.stem(mc)
                        if lemma in texte or stem in texte or mc in texte:
                            continue
                        else:
                            mono_multi_zero.append(mc)
                    else:
                        # phrasème
                        if mc not in texte:
                            mono_multi_zero.append(mc)
            dico_mono_traited[docn]=mono_multi_zero

    for k,v in dico_mono_traited.items():
        for e in v:
            print(k,'\t', e)    

def dico_mono_multi_lemm_stem_partoken(filein):
    # STEP 3 : segmenter les phrasèmes en tokens, si les tokens d'un phrasème existent dans le texte, on l'enlève des zero-occurrences    
    from nltk import word_tokenize
    from nltk.stem import SnowballStemmer
    fr = SnowballStemmer('french')
    import spacy
    sp = spacy.load("fr_core_news_sm")
    
    with open(filein, 'r') as infile:

        dico_mono_traited = {}
        
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        for rows in reader:
            docn = rows[0]
            with open('../pke/'+revue+'/'+revue+'_TRC_'+str(docn)+'.txt', 'r', encoding='utf-8') as txtfile:
                texte = txtfile.read().lower().replace('\n', '')
                mono_multi_zero = []
                for mc in rows[1].split(','):
                    if ' ' not in mc:
                        # mono
                        lemma = ''.join([token.lemma_ for token in sp(mc)])
                        stem = fr.stem(mc)
                        if lemma in texte or stem in texte or mc in texte:
                            continue
                        else:
                            mono_multi_zero.append(mc)
                    else:
                        # phrasème
                        for m in word_tokenize(mc):
                            lemma = ''.join([token.lemma_ for token in sp(m)])
                            stem = fr.stem(m)

                            if lemma in texte or stem in texte or mc in texte:
                                continue
                            else:
                                mono_multi_zero.append(mc)
            dico_mono_traited[docn]=mono_multi_zero

    for k,v in dico_mono_traited.items():
        for e in v:
            print(k,'\t', e)
# step1
# search_zero_occ(csv_to_dico('../data_pke/reference_keywords/lhomme.csv'))
# step 2
#dico_mono_lemm_stem('../data_pke/reference_keywords/lhomme.csv')
# step 3 
# dico_mono_lemm_stem_multi_partoken('../data_pke/reference_keywords/lhomme.csv')

def zero_in_numero(revue):
    # vérifier dans les titres de numéros, si y apparaissent les zero-occurrences
    import pandas as pd
    from langdetect import detect
    revue_csv = '../data_scraping/'+revue+'_tab_quote_all.csv'
    dataset = pd.read_csv(revue_csv, sep='\t')
    n = 1
    nb_zero_in_numero = 0
    for i in range(len(dataset)):
        langue = detect(str(dataset['article'][i])).upper()
        # print(langue)
        if langue != 'FR' or dataset['article'][i] == '' or pd.isnull(dataset['article'][i]):
            continue
        kw = dataset['motscles'][i] # string, liste de mots clés
        if type(kw) != float:
            kw = kw.replace(', ', ',').lower()
            kwl = kw.split(',')
            
            dfs = [dataset['titreDelArticle'][i], dataset['résumé(fr)'][i], dataset['article'][i]]
            text = ''
            for e in dfs:
                if type(e) != float:
                    text += e
                text += '\n'
            for e in kwl:
                if e not in text.lower() and (e in dataset['titreDuNuméro'][i].lower()):
                    print(f"mot-cle={e}, doc_n={n}, url={dataset['urlDelArticle'][i]}, titrenumero={dataset['titreDuNuméro'][i]}")
                    nb_zero_in_numero +=1
        n +=1

    print(f"nb_zero_in_numero={nb_zero_in_numero}")