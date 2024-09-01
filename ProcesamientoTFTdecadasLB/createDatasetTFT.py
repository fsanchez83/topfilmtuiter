'''
Created on 05 abr. 2023

@author: fsanchez
'''
# -*- coding: utf-8 -*-

import tmdbsimple as tmdb
import pandas as pd
import os.path
import yaml
import sys
from yaml.loader import SafeLoader

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']

lista_stats_base = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'.csv'
dataset_vprevia = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/dataset_'+id_lista+'.csv'
dataset_pbi = dataConfig['Resultados']['base_pbi']+'datasets/dataset_'+id_lista+'.csv'

tmdb.API_KEY = data['TMDB']['API_KEY']
pd.set_option('display.max_columns', None)
actualiza = False
lista_basica = pd.read_csv(lista_stats_base)

errores=[]

if os.path.exists(dataset_vprevia):
    actualiza = True
    print("##################### ACTUALIZA FICHERO ##################")
    lista_con_id = pd.read_csv(dataset_vprevia, sep=";")
    lista_basica = lista_basica.merge(lista_con_id.drop_duplicates(), on="url_peli", how='left', indicator=True)
    lista_basica = lista_basica[lista_basica['_merge'] == 'left_only'].reset_index()

Atributos_peli = ['Votos', "url_peli", "Id_peli", "Titulo", "Popularidad", 'Rating', 'Fecha', 'Duracion', 'Pais', 'Idioma',
                  'Presupuesto', 'Ganancia', 'Generos', 'Director', 'Genero_dir', 'Casting', 'Guion', 'Montaje', 'DOP',
                  'Resumen']
df_films = pd.DataFrame(columns=Atributos_peli)

search = tmdb.Search()
contador = 0

# for index, row in islice(lista_ratings.iterrows(), 1):
for index, row in lista_basica.iterrows():
    print(str(index)+": "+row['Title'])
    tmdb_type = row['tmdb_type']
    tmdb_id = row['tmdb_id']
    try:
        if tmdb_type == 'movie':
            movie = tmdb.Movies(tmdb_id)
            movieInfo = movie.info()
            votos = row['Review']
            url_peli = row['url_peli']
            id_peli = tmdb_id
            titulo = movieInfo['title']
            popularidad = movieInfo['popularity']
            rating = movieInfo['vote_average']
            fecha = movieInfo['release_date']
            duracion = movieInfo['runtime']
            idioma = movieInfo['original_language']
            productoras = movieInfo['production_companies']
            #productoras = movieInfo['production_countries']
            pais = ''
            paises=[]
            for paises_prod in productoras:
                if len(paises_prod['origin_country']) > 0:
                    paises.append(paises_prod['origin_country'])
            if ((idioma == 'en') & ('US' in paises)):
                pais = 'US'
            elif ((idioma == 'en') & ('GB' in paises)):
                pais = 'GB'
            elif idioma.upper() in paises:
                pais = idioma.upper()
            else:
                if len(paises) > 0:
                    pais = paises[0]
                else:
                    if len(movieInfo['production_countries']) > 0:
                        pais = movieInfo['production_countries'][0]['iso_3166_1']
                    else:
                        pais = ''

            ####### EXTRA SOLO PARA TFTCHINA(S) #############
            opciones = ['CN', 'TW', 'HK']
            pais = None

            # Buscamos el primer valor que coincida con alguno de 'CN', 'TW', 'HK'
            for p in paises:
                if p in opciones:
                    pais = p
                    break

            # Si no se encontró ninguno de los valores, se asigna el primer valor del array
            if pais is None:
                if len(paises) > 0:
                    pais = paises[0]
                else:
                    if len(movieInfo['production_countries']) > 0:
                        pais = movieInfo['production_countries'][0]['iso_3166_1']
                    else:
                        pais = ''


            # for paises in productoras:
            #     if len(paises['origin_country']) > 0:
            #         pais = paises['origin_country']
            #         break
            # if len(pais)==0:
            #     if len(movieInfo['production_countries']) > 0:
            #         pais = movieInfo['production_countries'][0]['iso_3166_1']
            #     else:
            #         pais = ''
            # print(pais)
            # sys.exit()
            # for paises in productoras:
            #     if len(paises['iso_3166_1']) > 0:
            #         pais = paises['iso_3166_1']
            #         break
            # if len(pais)==0:
            #     if len(movieInfo['production_companies']) > 0:
            #         pais = movieInfo['production_companies'][0]['origin_country']
            #     else:
            #         pais = ''
            presupuesto = movieInfo['budget']
            ganancia = movieInfo['revenue']
            resumen = movieInfo['overview'].replace('\n', ' ').replace('\r', ' ')
            generos = []
            for dic in movieInfo['genres']:
                generos.append(dic['name'])

            director = []
            director_genre = []
            guion = []
            montaje = []
            dop = []
            casting = []

            creditos = movie.credits()
            for dic in creditos['crew']:
                if dic['job'] == 'Director':
                    director.append(dic['name'])
                    director_genre.append(dic['gender'])
                if dic['job'] == 'Screenplay':
                    guion.append(dic['name'])
                if dic['job'] == 'Editor':
                    montaje.append(dic['name'])
                if dic['job'] == 'Director of Photography':
                    dop.append(dic['name'])

            for dic in creditos['cast']:
                casting.append(dic['name'])

            # if 1 in director_genre and 2 in director_genre:  # "Directores de ambos generos"
            #     genero_dir = 3
            # elif 2 in director_genre:  # "Director hombre"
            #     genero_dir = 2
            # elif 2 in director_genre:  # "Directora mujer"
            #     genero_dir = 1
            # else:  # "Género desconocido"
            #     genero_dir = 0

            lista_peli = [votos, url_peli, id_peli, titulo, popularidad, rating, fecha, duracion, pais, idioma,
                          presupuesto, ganancia, generos, director, director_genre, casting, guion, montaje, dop, resumen]

        if tmdb_type == 'tv':
            movie = tmdb.TV(tmdb_id)
            movieInfo = movie.info()
            votos = row['Review']
            url_peli = row['url_peli']
            id_peli = tmdb_id
            titulo = movieInfo['name']
            popularidad = movieInfo['popularity']
            rating = movieInfo['vote_average']
            fecha = movieInfo['first_air_date']
            try:
                duracion = movieInfo['number_of_episodes']*movieInfo['episode_run_time'][0]
            except IndexError:
                duracion = ''
            paises = movieInfo['production_countries']
            if len(paises) > 0:
                pais = paises[0]['name']
            else:
                pais = ''
            idioma = movieInfo['original_language']
            presupuesto = ''
            ganancia = ''
            resumen = movieInfo['overview'].replace('\n', ' ').replace('\r', ' ')
            generos = []
            for dic in movieInfo['genres']:
                generos.append(dic['name'])

            director = []
            director_genre = []
            guion = []
            montaje = []
            dop = []
            casting = []

            creditos = movie.credits()
            for dic in creditos['crew']:
                if dic['job'] == 'Director':
                    director.append(dic['name'])
                    director_genre.append(dic['gender'])
                if dic['job'] == 'Screenplay':
                    guion.append(dic['name'])
                if dic['job'] == 'Editor':
                    montaje.append(dic['name'])
                if dic['job'] == 'Director of Photography':
                    dop.append(dic['name'])

            if len(director) < 1:
                try:
                    director.append(movieInfo['created_by'][0]['name'])
                    director_genre.append(movieInfo['created_by'][0]['gender'])
                except IndexError:
                    director = []


            for dic in creditos['cast']:
                casting.append(dic['name'])

            # if 1 in director_genre and 2 in director_genre:  # "Directores de ambos generos"
            #     genero_dir = 3
            # elif 2 in director_genre:  # "Director hombre"
            #     genero_dir = 2
            # elif 2 in director_genre:  # "Directora mujer"
            #     genero_dir = 1
            # else:  # "Género desconocido"
            #     genero_dir = 0

            lista_peli = [votos, url_peli, id_peli, titulo, popularidad, rating, fecha, duracion, pais, idioma,
                          presupuesto, ganancia, generos, director, director_genre, casting, guion, montaje, dop, resumen]

        tamanioDF = len(df_films)
        df_films.loc[tamanioDF] = lista_peli

    except Exception as e:
        print("Error en el procesado de: "+row['Title'])
        errores.append(row['Title'])
        print(e)


if actualiza == True:
    pd.concat([lista_con_id, df_films]).to_csv(dataset_vprevia, sep=';', index=False)
    pd.concat([lista_con_id, df_films]).to_csv(dataset_pbi, sep=';', index=False)
else:
    df_films.to_csv(dataset_vprevia, sep=';', index=False)
    df_films.to_csv(dataset_pbi, sep=';', index=False)

print('Errores:')
print(errores)
print('FIN')
