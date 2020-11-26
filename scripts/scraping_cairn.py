#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Xin YU"

import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import re
import sys

"""
step 1 : Data scraping
collect articles of 8 journals in the sites openedition.org & cairn.info
12 element of each article : 
    number title
    number url
    number reference
    theme
    article title
    articles subtitle
    article url
    authors
    article body
    abstract
    keywords
    notes
Data is in ./data_scraping
"""

"""
Journals information
# annales --> Total : 92 numéros, 297 thèmes, 917 articles, 553 résumés en français.
# assr --> Total : 82 numéros, 114 thèmes, 3580 articles, 576 résumés en français.
# etudesafricaines --> Total : 62 numéros, 99 thèmes, 858 articles, 649 résumés en français.
# monderusse --> Total : 53 numéros, 129 thèmes, 704 articles, 475 résumés en français.
# etudesrurales --> Total : 38 numéros, 70 thèmes, 516 articles, 384 résumés en français.
# histoiremesure --> Total : 37 numéros, 83 thèmes, 341 articles, 237 résumés en français.
# lhomme --> Total : 61 numéros, 85 thèmes, 919 articles, 494 résumés en français.
# techniqueculture --> Total : 10 numéros, 33 thèmes, 227 articles, 114 résumés en français.
"""

def takeanap(link):
    # wait senconds for the refresh of a page
    page = ''
    while page == '':
        try:
            page = requests.get(link)
            break
        except:
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    return page
def clean(texte):
    new_texte = texte
    # replace multiple spaces|non-breaking space(=espace insécable) by a signle space
    new_texte = re.sub(r'\s+', ' ', new_texte)
    new_texte = new_texte.replace(u'\xa0', u' ')
    # delete " as the fact that the csv quoting is csv.QUOTE_ALL
    new_texte = new_texte.replace('"', '')
    return new_texte

def scraping_revue(revue):
    """
    revue : annales | assr | etudesafricaines | monderusse | etudesrurales | histoiremesure | lhomme | techniqueculture
    """
    with open(sys.argv[1], mode='w') as output_csv:
        # sys.argv[1] : csv file to save data --> data_scraping/revue_name.csv
        fieldnames = "thème\ttitreDuNuméro\tréférenceDuNuméro\turlDuNuméro\ttitreDelArticle\tsous-titre\tauteur(s)\turlDelArticle\trésumé(fr)\tarticle\tnotes\tmotscles\n"
        writer = csv.writer(output_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
        output_csv.write(fieldnames)

        # redirect to the page of journal/revue
        cairnurl = 'https://www.cairn.info/'
        revueurl = cairnurl + revue
        revuepage = requests.get(revueurl)
        revuesoup = BeautifulSoup(revuepage.content, 'html.parser')
        # locate the bloc of the list of numbers
        numeros = revuesoup.find('div', class_='list-grid')
        # recover titles and references of the numbers (reference : pubilication year + quarter)
        titres_numeros = numeros.find_all('li', class_='titre-numero')
        references = numeros.find_all('li', class_='reference')
        # counters : count numbers of articles, themes, journal numbers
        count_article = count_resume = 0
        count_theme = set()
        count_numero = 0

        for t,r in zip(titres_numeros, references):
            # get journal number title
            tn = clean(t.text.strip())
            # get journal reference information
            ref = r.text.strip()
            # get journal number url
            link_numero = cairnurl + t.find('a')['href']

            # verify if the journal number page is accessible, if not we ignore it
            # sometimes the editeur creates a bloc for a new journal number but the bloc is not available
            if link_numero == cairnurl + 'javascript:void(0);':
                continue

            # redirect to the page of a journal number, e.g. https://www.cairn.info/revue-annales-2020-1.htm
            numeropage = takeanap(link_numero)
            numero_soup = BeautifulSoup(numeropage.content, 'html.parser')
            count_numero += 1

            # regard title subdivisions as themes
            themes = numero_soup.find_all('h2', class_='title-subdivision')
            for theme in themes:
                # cases that theme doesn't existe
                if theme.text.strip() == '':
                    # if theme is absent, let journal number title be the theme
                    # e.g. https://www.cairn.info/revue-annales-2001-4.htm   https://www.cairn.info/revue-annales-2001-6.htm
                    # theme_article = t.text.strip()
                    theme_article = tn
                # cases that theme existe
                else:
                    if 'comptes rendu' in theme.text.strip().lower():
                        # if theme contains 'comptes rendu', let 'comptes rendus' be the theme
                        # e.g. https://www.cairn.info/revue-annales-2017-4.htm
                        # https://www.cairn.info/revue-annales-2015-3.htm
                        # https://www.cairn.info/revue-annales-2018-3.htm 
                        theme_article = 'comptes rendus'
                    else:
                        # collect themes
                        theme_article = theme.text.strip()
                theme_article = clean(theme_article)
                count_theme.add(theme_article)

                # Find next siblings until a certain one
                # https://stackoverflow.com/questions/11647348/find-next-siblings-until-a-certain-one-using-beautifulsoup
                for sib in theme.next_siblings:
                    # theme.next_siblings = blocs of article 
                    if sib.name == 'div':
                        print('thème\t', theme_article)
                        print(f'titres_numeros, references , link_numero : {tn} | {ref} | {link_numero}')
                        
                        # locate the article's title
                        titre_article = sib.find('li', class_='titre-article')
                        if titre_article:
                            titre_article = titre_article.text.strip().replace(u'\xa0', u' ')
                        else:
                            break
                        
                        # locate the article's subtitle
                        sous_titre = sib.find('li', class_='sous-titre')
                        if not sous_titre:
                            sous_titre = ''
                        else:
                            sous_titre = clean(sous_titre.text.strip())

                        # locate the article's authors
                        auteurs = sib.find('li', class_='auteurs')
                        if not auteurs:
                            auteurs = ''
                        else:
                            auteurs = clean(auteurs.text.strip())
                        
                        # # locate the article's url
                        link_article = sib.find('a')['href']
                        
                        # Scraping articles' informations : (1) in openedition.org ; (2) in cairn.info
                        motscles = ''
                        # scraping articles in openedition.org
                        if 'journals.openedition.org' in link_article or 'assr.revues.org' in link_article or 'etudesafricaines.revues.org' in link_article or 'monderusse.revues.org' in link_article or 'etudesrurales.revues.org' in link_article or 'histoiremesure.revues.org' in link_article or 'lhomme.revues.org' in link_article or 'tc.revues.org' in link_article:
                            # http://etudesrurales.revues.org/8022
                            # "http://assr.revues.org/25670"
                            # "http://journals.openedition.org/assr/27702"
                            # "http://etudesafricaines.revues.org/142"
                            
                            # redirect to the page of an article
                            article_page = takeanap(link_article)
                            article_soup = BeautifulSoup(article_page.content, 'html.parser')
                            resume = article_soup.find('div', class_='tabContent', lang='fr')
                            motsclesindex = article_soup.find('div', id='entries')
                            article_body = article_soup.find('div', class_='wResizable')
                            notes = article_soup.find('div', id='notes')
                            # bibliographie = article_soup.find('div', id='bibliography')
                            
                            if article_body:
                                # if article body existe, scraping the body of article
                                ps = article_body.select('.texte, .citation')
                                psl = []
                                for p in ps:
                                    # scraping each paragraph

                                    # collect paragraphe text but not number
                                    unwanted_nopara = p.find('span', class_='paranumber')
                                    if unwanted_nopara:
                                        unwanted_nopara.extract()
                                    p = clean(p.text.strip())
                                    psl.append(p)
                                article_body = ' '.join(psl)
                            else:
                                # ignore pdf version
                                article_body = ''
                            
                            if notes:
                                # scraping notes
                                notes = clean(notes.text.strip()[6:])
                                notes = notes.replace('Haut de page', '')
                            else:
                                notes = ''
                            # if bibliographie:
                                #bibliographie = clean(bibliographie.text.strip()[15:-14])
                            #else:
                                #bibliographie = ''
                            
                            if resume:
                                # scraping abstract
                                resume = clean(resume.text.strip())
                                count_resume += 1
                            else:
                                resume = ''
                            
                            if motsclesindex:
                                # scraping french keywords
                                motsclesindexdiv = motsclesindex.find_all('div', class_='index')
                                motscles = motsclesindexdiv[0].text.strip()[11:]
                        
                        # scraping articles in cairn.info
                        else:
                            link_article = cairnurl + link_article
                            article_page = takeanap(link_article)
                            article_soup = BeautifulSoup(article_page.content, 'html.parser')
                            # version 1 d'extraction des articles
                            article_body = article_soup.find('div', class_='corps')
                            if article_body:
                                ps = article_body.select('.para, .bloccitation')
                                psl = []
                                # Exclude unwanted tag on Beautifulsoup Python : https://stackoverflow.com/questions/40760441/exclude-unwanted-tag-on-beautifulsoup-python
                                for p in ps:
                                    unwanted_notes = p.find('a', class_='amorce')
                                    if unwanted_notes:
                                        unwanted_notes.extract() 
                                    unwanted_nopara = p.find('a', class_='no-para')
                                    if unwanted_nopara :
                                        unwanted_nopara.extract() 
                                    p = clean(p.text.strip())
                                    psl.append(p)
                                article_body = ' '.join(psl)
                            else:
                                article_body = ''
                            #print('link_article:\t', link_article)
                            # print('--------article\n', article_body)
                            # writer.writerow([link_article, article_body])

                            # scraping notes
                            notes = article_soup.find('ul', class_='wrapper-children-grnote')
                            if notes:
                                # notes = re.sub(r'[ \t\r\f]+', ' ', notes.text.strip())
                                notes = clean(notes.text.strip())
                                notes = re.sub(r']\s+', '] ', notes)
                            else :
                                notes = ''
                            #print('--------notes\n', notes)
                            
                            
                            resume_tab = article_soup.find(id='tab-resume')
                            if resume_tab:
                                resume_link = link_article + '?contenu=resume'
                                resume_page = requests.get(resume_link)
                                resume_soup = BeautifulSoup(resume_page.content, 'html.parser')
                                resume_fr = resume_soup.find('div', class_='resume lang-fr')
                                # print('resume_link:\t', resume_link)
                                count_resume += 1

                                # scraping french abstract
                                if resume_fr:
                                    resume = resume_fr.find('div', class_='corps')
                                    if resume:
                                        resume = clean(resume.text.strip())
                                    else:
                                        resume = ''
                                    # scraping french keywords
                                    motsclesliste = resume_fr.find('div', class_='grmotcle lang-fr')
                                    if motsclesliste:
                                        motsclesli = motsclesliste.find_all('li', class_= 'motcle')
                                        motscles = ', '.join([mc.text.strip() for mc in motsclesli])
                            else:
                                resume = ''
                            # bibliographie = ''
                        
                        print(f'titre, auteurs, link_article : {titre_article} | {auteurs} | {link_article}')
                        count_article += 1
                        writer.writerow([theme_article, tn, ref, link_numero, titre_article, sous_titre, auteurs, link_article, resume, article_body, notes, motscles])
                        time.sleep(2)
                    elif sib.name == 'h2':
                        break
                print("-"*10, "FIN D'UN THEME")
            
            print("*"*20, f"FIN DU NUMERO {count_numero}")

        print(f'Total : {count_numero} numéros, {len(count_theme)} thèmes, {count_article} articles, {count_resume} résumés en français.')

if __name__ == '__main__':
    scraping_revue('annales')
    