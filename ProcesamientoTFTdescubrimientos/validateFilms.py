'''
Created on 05 abr. 2023

@author: fsanchez
'''
# -*- coding: utf-8 -*-

import tmdbsimple as tmdb
import pandas as pd
import sys
import os.path
import requests as rq
from bs4 import BeautifulSoup
import yaml
from yaml.loader import SafeLoader

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']
filmid_whitelist = pd.read_csv('filmid_whitelist_tft')

lista_completa_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'_bruto.csv'
lista_completa_pbi_bruto = dataConfig['Resultados']['base_pbi']+'listas_votaciones/Lista_votaciones_'+id_lista+'_bruto.csv'
lista_stats_base_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'_bruto.csv'
lista_stats_base_lb_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_lb_bruto.csv'

lista_completa = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'.csv'
lista_completa_pbi = dataConfig['Resultados']['base_pbi']+'listas_votaciones/Lista_votaciones_'+id_lista+'.csv'
lista_stats_base = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'.csv'
lista_stats_base_lb = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_lb.csv'


pd.set_option('display.max_columns', None)

lista_basica = pd.read_csv(lista_stats_base_bruto)
lista_info_LB = pd.DataFrame(columns=['Title', 'Year', 'url_peli', 'Review', 'tmdb_type', 'tmdb_id', 'nviews'])

errores=[]

def get_LBData(url_film):
    url_base = 'https://letterboxd.com'
    url = url_base + url_film
    url_stats = url_base + '/esi' + url_film + 'stats/'
    page = rq.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    try:
        literal = soup.find_all("a", {"data-track-action": "TMDb"})[0].get('href').split('themoviedb.org/')[1].split(
            '/')
        tmdb_type = literal[0]
        tmdb_id = literal[1]
    except:
        tmdb_type = 0
        tmdb_id = 0
        errores.append(url_film)

    pagestats = rq.get(url_stats)
    soupstats = BeautifulSoup(pagestats.content, 'html.parser')
    nviews = int(soupstats.find('a', class_='has-icon icon-watched icon-16 tooltip').get('title').split()[2].replace(',',''))
    return tmdb_type, tmdb_id, nviews

# for index, row in islice(lista_ratings.iterrows(), 1):
for index, row in lista_basica.iterrows():
    print(str(index)+": "+row['Title'])
    if row['url_peli'] in set(filmid_whitelist['url_peli']):
        print('Esta entrando en la Whitelist')
        tmdb_type = filmid_whitelist[filmid_whitelist['url_peli'] == row['url_peli']]['Type'].values[0]
        tmdb_id = filmid_whitelist[filmid_whitelist['url_peli'] == row['url_peli']]['Id'].values[0]
    else:
        tmdb_type, tmdb_id, nviews = get_LBData(row['url_peli'])

    datos_peli = [row['Title'], row['Year'], row['url_peli'], row['Review'], tmdb_type, tmdb_id, nviews]
    lista_info_LB.loc[len(lista_info_LB)] = datos_peli

lista_descartes = lista_info_LB[lista_info_LB['nviews'] > 999]
lista_info_LB = lista_info_LB.drop(lista_info_LB[lista_info_LB['nviews'] > 999].index)

print(lista_info_LB)
print('Errores:', errores)
print(lista_descartes)

# Dejamos los resultados filtrados en los csv limpios

df_lista_completa_bruto = pd.read_csv(lista_completa_bruto)
df_lista_completa = df_lista_completa_bruto[df_lista_completa_bruto['url_peli'].isin(lista_info_LB['url_peli'])]
df_lista_completa = df_lista_completa.rename(columns={'Unnamed: 0': ''})

df_lista_completa_pbi_bruto = pd.read_csv(lista_completa_pbi_bruto)
df_lista_completa_pbi = df_lista_completa_pbi_bruto[df_lista_completa_pbi_bruto['url_peli'].isin(lista_info_LB['url_peli'])]
df_lista_completa_pbi = df_lista_completa_pbi.rename(columns={'Unnamed: 0': ''})

df_lista_stats_base_lb_bruto = pd.read_csv(lista_stats_base_lb_bruto)
df_lista_stats_base_lb = df_lista_stats_base_lb_bruto.merge(lista_info_LB, on=['Title', 'Year'], how='inner')
df_lista_stats_base_lb = df_lista_stats_base_lb.rename(columns={'Review_x': 'Review'})[df_lista_stats_base_lb_bruto.columns]

lista_info_LB.to_csv(lista_stats_base, index=False)
df_lista_completa.to_csv(lista_completa, index=False)
df_lista_completa_pbi.to_csv(lista_completa_pbi, index=False)
df_lista_stats_base_lb.to_csv(lista_stats_base_lb, index=False)
lista_descartes.to_csv('descartes.csv', index=False)

print('FIN')
