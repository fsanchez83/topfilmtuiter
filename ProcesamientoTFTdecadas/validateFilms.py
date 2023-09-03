'''
Created on 05 abr. 2023

@author: fsanchez
'''
# -*- coding: utf-8 -*-

import pandas as pd
import yaml
from yaml.loader import SafeLoader

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']
filmid_whitelist = pd.read_csv('filmid_whitelist_tft')

lista_completa_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'_bruto.csv'
lista_stats_base_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'_bruto.csv'
lista_stats_base_lb_bruto = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_lb_bruto.csv'

lista_completa = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'.csv'
lista_completa_pbi = dataConfig['Resultados']['base_pbi']+'listas_votaciones/Lista_votaciones_'+id_lista+'.csv'
lista_stats_base = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'.csv'
lista_stats_base_lb = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_lb.csv'
lista_stats_base_pbi = dataConfig['Resultados']['base_pbi']+'stats/Stats_'+id_lista+'.csv'


pd.set_option('display.max_columns', None)

lista_basica = pd.read_csv(lista_stats_base_bruto)

# Lista de peliculas que no cumplen los requisitos
lista_descartes = lista_basica[(lista_basica['Year'] > dataConfig['Decadas']['anno_fin']) | (lista_basica['Year'] < dataConfig['Decadas']['anno_ini'])]

# Descartar peliculas que no cumplen los requisitos
lista_info_LB_1 = lista_basica.drop(lista_basica[lista_basica['Year'] < dataConfig['Decadas']['anno_ini']].index)
lista_info_LB = lista_info_LB_1.drop(lista_info_LB_1[lista_info_LB_1['Year'] > dataConfig['Decadas']['anno_fin']].index)

print(lista_info_LB)
print(lista_descartes)

# Dejamos los resultados filtrados en los csv limpios

df_lista_completa_bruto = pd.read_csv(lista_completa_bruto)
df_lista_completa = df_lista_completa_bruto[df_lista_completa_bruto['url_peli'].isin(lista_info_LB['url_peli'])]
df_lista_completa = df_lista_completa.rename(columns={'Unnamed: 0': ''})

df_lista_completa_pbi_bruto = pd.read_csv(lista_completa_bruto)
df_lista_completa_pbi = df_lista_completa_pbi_bruto[df_lista_completa_pbi_bruto['url_peli'].isin(lista_info_LB['url_peli'])]
df_lista_completa_pbi = df_lista_completa_pbi.rename(columns={'Unnamed: 0': ''})

df_lista_stats_base_lb_bruto = pd.read_csv(lista_stats_base_lb_bruto)
df_lista_stats_base_lb = df_lista_stats_base_lb_bruto.merge(lista_info_LB, on=['Title', 'Year'], how='inner')
df_lista_stats_base_lb = df_lista_stats_base_lb.rename(columns={'Review_x': 'Review'})[df_lista_stats_base_lb_bruto.columns]

lista_info_LB.to_csv(lista_stats_base, index=False)
lista_info_LB.to_csv(lista_stats_base_pbi, index=False)
df_lista_completa.to_csv(lista_completa, index=False)
df_lista_completa_pbi.to_csv(lista_completa_pbi, index=False)
df_lista_stats_base_lb.to_csv(lista_stats_base_lb, index=False)
lista_descartes.to_csv('descartes.csv', index=False)

print('FIN')
