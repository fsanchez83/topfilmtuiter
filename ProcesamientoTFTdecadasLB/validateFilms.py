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
import html
import random
import time

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

anno_ini = dataConfig['Decadas']['anno_ini']
anno_fin = dataConfig['Decadas']['anno_fin']

id_lista = dataConfig['General']['id_lista']
filmid_whitelist = pd.read_csv('filmid_whitelist_tft')
filmid_db_url = dataConfig['Resultados'][
                            'resultados_base']+'Globales/LB-TMDB.csv'
filmid_db = pd.read_csv(filmid_db_url)

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
#lista_info_LB = pd.DataFrame(columns=['Title', 'Year', 'url_peli', 'Review',
# 'tmdb_type', 'tmdb_id', 'nviews'])

errores=[]

def get_LBData(url_film):
    url_base = 'https://letterboxd.com'
    url = url_base + url_film
    url_stats = url_base + '/csi' + url_film + 'stats/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    delay = random.uniform(1, 2)  # entre 1 y 2 segundos
    time.sleep(delay)
    page = rq.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    try:
        literal = soup.find_all("a", {"data-track-action": "TMDB"})[0].get(
            'href').split('themoviedb.org/')[1].split(
            '/')
        tmdb_type = literal[0]
        tmdb_id = literal[1]
    except:
        print('falla')
        tmdb_type = 0
        tmdb_id = 0
        errores.append(url_film)

    #pagestats = rq.get(url_stats)
    #soupstats = BeautifulSoup(pagestats.content, 'html.parser')
    #nviews = int(soupstats.find('a', class_='has-icon icon-watched icon-16
    # tooltip').get('title').split()[2].replace(',',''))
    return tmdb_type, tmdb_id


import pandas as pd


def enrich_lista_basica(lista_basica, filmid_whitelist, filmid_db, get_LBData,
                        update_db=True, db_csv_path=None):
    """
    Enriquecer lista_basica con tmdb_type y tmdb_id.
    - Prioridad: filmid_whitelist > filmid_db > get_LBData.
    - Si update_db=True, añade los nuevos resultados a filmid_db.
    - Si db_csv_path se indica, guarda filmid_db actualizado en ese CSV.
    - Conserva 'Year' y 'Title' de lista_basica en el resultado.
    """

    # --- 1. Normalizamos columnas ---
    filmid_whitelist = filmid_whitelist.rename(
        columns={"Type": "tmdb_type", "Id": "tmdb_id"})

    # --- 2. Join con whitelist ---
    df = lista_basica.merge(
        filmid_whitelist[["url_peli", "tmdb_type", "tmdb_id"]],
        on="url_peli", how="left", suffixes=("", "_wl")
    )

    # --- 3. Join con DB ---
    df = df.merge(
        filmid_db[["url_peli", "tmdb_type", "tmdb_id"]],
        on="url_peli", how="left", suffixes=("", "_db")
    )

    # --- 4. Resolver ---
    new_entries = []

    def resolve(row):
        if pd.notnull(row["tmdb_type"]):  # whitelist
            return row["tmdb_type"], row["tmdb_id"]
        elif pd.notnull(row["tmdb_type_db"]):  # db
            return row["tmdb_type_db"], row["tmdb_id_db"]
        else:  # API
            tmdb_type, tmdb_id = get_LBData(row["url_peli"])
            new_entries.append({"url_peli": row["url_peli"],
                                "tmdb_type": tmdb_type,
                                "tmdb_id": tmdb_id})
            return tmdb_type, tmdb_id

    df[["tmdb_type_final", "tmdb_id_final"]] = df.apply(
        lambda row: pd.Series(resolve(row)), axis=1
    )

    # --- 5. Actualizar DB ---
    if update_db and new_entries:
        new_df = pd.DataFrame(new_entries)
        filmid_db = pd.concat([filmid_db, new_df], ignore_index=True).drop_duplicates(
            subset=["url_peli"], keep="last"
        )
        if db_csv_path:
            filmid_db.to_csv(db_csv_path, index=False, encoding="utf-8")

    # --- 6. Resultado ---
    enriched = df[["url_peli", "Title", "Year", "tmdb_type_final",
                   "tmdb_id_final"]].rename(
        columns={"tmdb_type_final": "tmdb_type", "tmdb_id_final": "tmdb_id"}
    )

    if update_db:
        return enriched, filmid_db
    else:
        return enriched


result, filmid_db_actualizado = enrich_lista_basica(
    lista_basica,
    filmid_whitelist,
    filmid_db,
    get_LBData,
    update_db=True,
    db_csv_path=filmid_db_url
)

def incluyeElectores(df_lista_completa, df_lista_stats_base_lb):

    # --- Paso 1: extraer usuario de la url ---
    df_lista_completa["usuario"] = df_lista_completa["url"].str.extract(
        r"letterboxd\.com/([^/]+)/")

    # --- Paso 2: agrupar usuarios por película con links en HTML ---
    def build_links(group):
        # ordenar desc por Puntos
        group = group.sort_values("Puntos", ascending=False)
        # agrupar por Puntos y generar string
        parts = []
        for puntos, sub in group.groupby("Puntos", sort=False):
            links = ", ".join(f"<a href='{url}'>{html.escape(u)}</a>"
                              for u, url in zip(sub["usuario"], sub["url"]))
            parts.append(f"{puntos} puntos: {links}")
        return " <br> ".join(parts)

    df_users = (
        df_lista_completa
        .dropna(subset=["url", "usuario", "Puntos"])
        .groupby(["Titulo", "Anio"])
        .apply(build_links)
        .reset_index(name="usuarios_links")
    )

    # --- Paso 3: unir con stats ---
    df_lista_stats_base_lb = df_lista_stats_base_lb.rename(
        columns={"Title": "Titulo", "Year": "Anio"})
    df_final = df_lista_stats_base_lb.merge(df_users, on=["Titulo", "Anio"], how="left")

    # --- Paso 4: añadir al campo Review ---
    df_final["Review"] = df_final.apply(
        lambda row: f'{row["Review"]}. Elegida por:<p>{row["usuarios_links"]}'
        if pd.notna(row["usuarios_links"]) else f'{row["Review"]} votos',
        axis=1
    )
    df_final = df_final[["Titulo", "Anio", "Review"]].rename(columns={"Titulo": "Title", "Anio": "Year"})


    return df_final

print(result)

lista_descartes = result[(result['Year'] > anno_fin) | (result['Year'] < anno_ini)]
lista_info_LB = result[(result['Year'] >= anno_ini) & (result['Year'] <= anno_fin)]

lista_info_LB = result # Si no se descarta ninguna pelicula. Comentar para decadas

print(lista_info_LB)
print('Errores:', errores)
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

df_lista_stats_base_lb = incluyeElectores(df_lista_completa, df_lista_stats_base_lb)

lista_info_LB.to_csv(lista_stats_base, index=False)
lista_info_LB.to_csv(lista_stats_base_pbi, index=False)
df_lista_completa.to_csv(lista_completa, index=False)
df_lista_completa_pbi.to_csv(lista_completa_pbi, index=False)
df_lista_stats_base_lb.to_csv(lista_stats_base_lb, index=False)
lista_descartes.to_csv('descartes.csv', index=False)

print('FIN')