#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

import pandas as pd
import sys
import os
import csv

# extraire des données nécesaires afin de les importer dans l'outil Gargantext

# load dataset from csv
separateur = '\t'
filecsv = sys.argv[1] # '../data_scraping/NOM_DU_FICHIER.csv'
df = pd.read_csv(filecsv, sep =separateur, na_filter=False)

df['title'] = df['titreDelArticle'].replace(to_replace='[“”]', value='', regex=True)
df['abstract'] = df['résumé(fr)'].astype(str) + df['article']
df['publication_year'] = df['réréfenceDuNuméro'].replace(to_replace='/.*', value='', regex=True)
df.rename(columns={'auteur(s)':'authors', 'titreDuNuméro':'source'}, inplace=True)
df['publication_month'] = df['réréfenceDuNuméro'].str.extract(r'\d+/(\d)')
df['publication_day'] = '1'

df = df.drop(columns=['réréfenceDuNuméro', 'titreDelArticle', 'sous-titre', 'résumé(fr)', 'article', 'thème', 'urlDuNuméro', 'urlDelArticle', 'notes', 'motscles'])

print(df.columns, df.shape)
print(df.head(5))
# write 
outcsv = sys.argv[2] # './data_gargantext/NOM_DU_FICHIER.csv'
df.to_csv(outcsv, sep=separateur, quotechar='"', quoting=csv.QUOTE_ALL, index=False)