#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

import spacy
import csv
nlp = spacy.load("fr_core_news_sm")

"""
use Spacy to extract keywords' POS tagging

input : csv file that contains document numbers and keywords assigned to each document
output exemple in ../data_additional/spacy_pos
"""

def extract_keyword_pos(revue):
    # extract POS tagging of keywords
    mc_csv = '../data_pke/reference_keywords/'+revue+'.csv'
    with open(mc_csv, encoding="utf-8") as infile:
        reader = csv.reader(infile, delimiter='\t')
        headers=next(reader)
        for rows in reader:
            mcs = rows[1].split(',')
            # print(mcs)
            for mc in mcs:
                doc = nlp(mc)
                if ' ' in mc or '/' in mc or '-' in mc:
                    print('\t',mc, end='\t')
                    for token in doc:
                        print(token.pos_, end=' ')
                    print('\n')
                else:
                    for token in doc:
                        print('\t', token, '\t', token.pos_)

def pos_count(pos_filein, pos_fileout):
    # count POS tagging
    # pos_filein : file producted by function extract_keyword_pos(revue)
    dico = {}
    with open(pos_only_filein, encoding='utf-8') as f:
        for line in f:
            m = line.strip()
            if m in dico:
                dico[m] +=1
            else:
                dico[m] =1

    with open(pos_only_fileout, 'w', encoding='utf-8') as out:
        for k, v in dico.items():
            line = k+'\t'+str(v)+'\n'
            out.write(line)

pos_count('histoiremesure_spacy_pos.txt', 'histoiremesure_spacy_pos_out.txt')