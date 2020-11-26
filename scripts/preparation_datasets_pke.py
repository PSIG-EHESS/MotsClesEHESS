#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

"""
Step 2 : preparation datasets for PKE
    task 1 : extract keywords in csv file
    task 2 : extract 4 elements of articles in txt file

revue : annales | assr | etudesafricaines | monderusse | etudesrurales | histoiremesure | lhomme | techniqueculture
"""

import sys
import pandas as pd
from langdetect import detect
import re
import csv

input_dir = './data_scraping/'
output_directory_keywords = './data_pke/reference_keywords/'
output_directory_articles = './data_pke/pke/articles/'
def extract_keywords(revue):
    """
    extract keywords of a journal in a csv file
    csv file has 2 columns : col1 --> document number, col2 --> reference keywords of that document
    csv_dir : directory that contains csv files produced by step 1
    revue : annales | assr | etudesafricaines | monderusse | etudesrurales | histoiremesure | lhomme | techniqueculture
    """
    # extract keywords of a journal in a csv file
    input_csv_file = input_dir + nomrevue + '.csv'
    dataset = pd.read_csv(input_csv_file, sep='\t')
    n = 1

    with open(output_directory_keywords + revue +'.csv', 'w', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['doc_n', 'motsclés_existants'])
        
        for i in range(len(dataset)):
            # identify articles' language
            langue = detect(str(dataset['article'][i])).upper()
            # ignore articles that are not in french
            if langue != 'FR' or dataset['article'][i] == '' or pd.isnull(dataset['article'][i]):
                continue

            kw = dataset['motscles'][i]
            if type(kw) != float:
                kw = kw.replace(', ', ',')
                writer.writerow([n, kw.lower()])
            n += 1

def extract_texts(revue):
    """
    extract each article in a .txt file
    """
    input_csv_file = input_dir + revue + '.csv'
    dataset = pd.read_csv(input_csv_file, sep='\t')
    n = 1
    for i in range(len(dataset)):
        langue = detect(str(dataset['article'][i])).upper()
        # print(langue)
        if langue != 'FR' or dataset['article'][i] == '' or pd.isnull(dataset['article'][i]):
            # print(dataset['titreDelArticle'][i])
            continue

        # extract 4 elements
        dfs = [dataset['titreDuNuméro'][i],dataset['titreDelArticle'][i],dataset['sous-titre'][i], dataset['résumé(fr)'][i], dataset['article'][i]]
        text = ''
        for e in dfs:
            if type(e) != float:
                text += e
            text += '\n'
        text = re.sub("’", "'", text)
        
        output_file_trc = output_directory +revue +'/' + revue + '_NTSRC_' + str(n) + '.txt'
        output_file = open(output_file_trc, 'w', encoding='utf-8')
        output_file.write(text.strip())
        output_file.close()
        
        n += 1
    print('Il y a au total ' + str(n-1) + ' fichiers.')  

if __name__ == "__main__":
    extract_keywords('lhomme')

