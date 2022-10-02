
# -*- coding: utf-8 -*-

import tmdbsimple as tmdb
import pandas as pd
import sys
import os.path

tmdb.API_KEY = 'COMPLETAR'

# Se incluye una lista blanca para forzar el id de determinadas películas

filmid_whitelist=pd.read_csv('filmid_whitelist')
whitelist=filmid_whitelist[['Title','Year']]
lista_basica = pd.read_csv('Lista_votaciones_stats.csv')

Atributos_peli = ['Votos', "Id_peli", "Titulo", "Popularidad", 'Rating', 'Fecha', 'Duracion', 'Pais', 'Idioma',
                  'Presupuesto', 'Ganancia', 'Generos', 'Director', 'Casting', 'Guion', 'Montaje', 'DOP', 'Resumen']
df_films = pd.DataFrame(columns=Atributos_peli)

search = tmdb.Search()
contador = 0

# Bucle que recorre las pelis de la lista hasta llegar a la ultima metida en el dataset

# for index, row in islice(lista_ratings.iterrows(), 1):
for index, row in lista_basica.iterrows():


    # Se lanza una query a TMDB con titulo y anio para averiguar el id de la peli y datos basicos

    try:
        response = search.movie(query=row['Title'], year=row['Year'])
        tipo = ""
        hace_match = 0
        ## Pruebo match exacto en cine
        for opciones in response['results']:
            if row['Title'] == opciones['title']:
                hace_match = 1
                id_peli = opciones['id']
                titulo = row['Title']
                votos = row['Review']
                tipo = "cine"
                break

        if hace_match == 0:
            ## Pruebo match exacto en tv
            responsetv = search.tv(query=row['Title'], year=row['Year'])
            for opciones in responsetv['results']:
                if row['Title'] == opciones['name']:
                    if opciones['backdrop_path'] is None:
                        break
                    hace_match = 1
                    print('Hace match exacto en tv: ',row['Title'])
                    id_peli = opciones['id']
                    titulo = row['Title']
                    votos = row['Review']
                    tipo = "tv"
                    break

        if hace_match == 0:
            ## Pruebo match parcial en cine
            try:
                id_peli = response['results'][0]['id']
                print('Hace match parcial en cine: ', row['Title'])
            except:
                print('Pelicula no encontrada: '+row['Title'])
            titulo = row['Title']
            votos = row['Review']
            tipo = "cine"


            # Nueva consulta a TMDB para sacar detalles de la pelicula
        generos = []
        ## Si la película está en la lista blanca, cojo el id manualmente ###
        if whitelist.isin([row['Title'], row['Year']]).any().all():
            id_peli=filmid_whitelist.loc[(filmid_whitelist['Title'] == row['Title']) & (filmid_whitelist['Year'] == row['Year']),'Id'].item()
            tipo = filmid_whitelist.loc[(filmid_whitelist['Title'] == row['Title']) & (filmid_whitelist['Year'] == row['Year']),'Type'].item()
            print(row['Title']+' - Pelicula de la lista blanca con id: '+str(id_peli))
        #####################################################################
        if tipo == "cine":
            movie = tmdb.Movies(id_peli)
            response = movie.info()
            presupuesto = response['budget']
            ganancia = response['revenue']
            duracion = response['runtime']
        else:
            movie = tmdb.TV(id_peli)
            response = movie.info()
            presupuesto = 0
            ganancia = 0
            duracion = 0

        director = []
        guion = []
        dop = []
        montaje = []
        casting = []

        response = movie.info()
        #fecha = response['release_date']
        fecha = row['Year']
        resumen = response['overview']
        popularidad = response['popularity']
        rating = response['vote_average']
        if tipo == 'tv':
            try:
                director = "['"+response['created_by'][0]['name']+"']"
            except IndexError:
                director = []
        for dic in response['genres']:
            generos.append(dic['name'])

        if len(response['production_countries']) > 0:
            pais = response['production_countries'][0]['name']
        else:
            pais = []
        if len(response['spoken_languages']) > 0:
            idioma = response['spoken_languages'][0]['name']
        else:
            idioma = []




            # Nueva consulta a TMDB para sacar detalles del crew y del reparto

        response = movie.credits()
        for dic in response['crew']:
            if dic['job'] == 'Director':
                director.append(dic['name'])
            if dic['job'] == 'Screenplay':
                guion.append(dic['name'])
            if dic['job'] == 'Editor':
                montaje.append(dic['name'])
            if dic['job'] == 'Director of Photography':
                dop.append(dic['name'])

        for dic in response['cast']:
            casting.append(dic['name'])

        lista_peli = [votos, id_peli, titulo, popularidad, rating, fecha, duracion, pais, idioma,
                          presupuesto, ganancia, generos, director, casting, guion, montaje, dop, resumen]

        df_tamanio = len(df_films)
        df_films.loc[df_tamanio] = lista_peli

    except UnicodeEncodeError:
        print("Error en el nombre")

df_films.to_csv('dataset_topfilmtuiter.csv', sep=';', index=False)

print('FIN')

