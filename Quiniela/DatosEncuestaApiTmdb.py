"""
Created on 1 may 2023

@author: Faustino Sanchez Garcia
"""
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import yaml
from yaml.loader import SafeLoader
import time

pd.set_option('display.max_columns', 20)

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

api_key = data['TMDB']['API_KEY']

url_base = 'https://api.themoviedb.org/3/discover/movie?api_key='+api_key+'&language=en-US&sort_by=popularity.desc'
# tmdb.API_KEY = api_key

# 1. Griffith. 100036
print('griffith')
griffith = []
id_crew = 100036
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url+'&page='+str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        griffith.append(pelis['title'])
    time.sleep(2)

# 2. Feuillade. 102844
print('feuillade')
feuillade = []
id_crew = 102844
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url+'&page='+str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        feuillade.append(pelis['title'])
    time.sleep(2)

# 3. Bauer. 1004602
print('bauer')
bauer = []
id_crew = 1004602
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url+'&page='+str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        bauer.append(pelis['title'])
    time.sleep(2)


# 4. Sjostrom. 8741
print('sjostrom')
sjostrom = []
id_crew = 8741
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url+'&page='+str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        sjostrom.append(pelis['title'])
    time.sleep(2)

# 5. Chaplin. 13848
print('chaplin')
chaplin = []
id_crew = 13848
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url+'&page='+str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        chaplin.append(pelis['title'])
    time.sleep(2)

# 6. Weber. 1037794
print('weber')
weber = []
id_crew = 1037794
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url + '&page=' + str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        weber.append(pelis['title'])
    time.sleep(2)

# 7. Alice Guy. 1071403
print('guy')
guy = []
id_crew = 1071403
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_crew=' + str(id_crew)
    director = requests.get(url + '&page=' + str(n)).json()
    paginas = director['total_pages']
    resdirector = director['results']
    for pelis in resdirector:
        guy.append(pelis['title'])
    time.sleep(2)

# 8. Western. 37
print('western')
western = []
id_genre = 37
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_genres='+str(id_genre)
    genero = requests.get(url + '&page=' + str(n)).json()
    paginas = genero['total_pages']
    resgenero = genero['results']
    for pelis in resgenero:
        western.append(pelis['title'])
    time.sleep(2)


# 9. Terror. 27
print('terror')
terror = []
id_genre = 27
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_genres='+str(id_genre)
    genero = requests.get(url + '&page=' + str(n)).json()
    paginas = genero['total_pages']
    resgenero = genero['results']
    for pelis in resgenero:
        terror.append(pelis['title'])
    time.sleep(2)

# 10. Ciencia-ficción. 878
print('ciencia ficcion')
scifi = []
id_genre = 878
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_genres='+str(id_genre)
    genero = requests.get(url + '&page=' + str(n)).json()
    paginas = genero['total_pages']
    resgenero = genero['results']
    for pelis in resgenero:
        scifi.append(pelis['title'])
    time.sleep(2)

# 11. Animación. 16
print('animacion')
animation = []
id_genre = 16
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_genres='+str(id_genre)
    genero = requests.get(url + '&page=' + str(n)).json()
    paginas = genero['total_pages']
    resgenero = genero['results']
    for pelis in resgenero:
        animation.append(pelis['title'])
    time.sleep(2)

# 12. Cine primitivo I: siglo XIX
print('origenes1')
primi1 = []
rango_inf = 1870
rango_sup = 1900
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte='+str(rango_sup)+'&primary_release_date.gte='+str(rango_inf)
    rangos = requests.get(url + '&page=' + str(n)).json()
    paginas = rangos['total_pages']
    resrangos = rangos['results']
    for pelis in resrangos:
        primi1.append(pelis['title'])
    time.sleep(2)

# 13. Cine primitivo II: 1900-1904
print('origenes2')
primi2 = []
rango_inf = 1900
rango_sup = 1905
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte='+str(rango_sup)+'&primary_release_date.gte='+str(rango_inf)
    rangos = requests.get(url + '&page=' + str(n)).json()
    paginas = rangos['total_pages']
    resrangos = rangos['results']
    for pelis in resrangos:
        primi2.append(pelis['title'])
    time.sleep(2)

# 14. Cine primitivo III: 1905-1909
print('origenes3')
primi3 = []
rango_inf = 1905
rango_sup = 1910
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte='+str(rango_sup)+'&primary_release_date.gte='+str(rango_inf)
    rangos = requests.get(url + '&page=' + str(n)).json()
    paginas = rangos['total_pages']
    resrangos = rangos['results']
    for pelis in resrangos:
        primi3.append(pelis['title'])
    time.sleep(2)

# 15. Italia. it
print('italia')
italia = []
id_idioma = 'it'
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_original_language='+id_idioma
    pais = requests.get(url + '&page=' + str(n)).json()
    paginas = pais['total_pages']
    respais = pais['results']
    for pelis in respais:
        italia.append(pelis['title'])
    time.sleep(2)

# 16. Dinamarca. da
print('dinamarca')
dinamarca = []
id_idioma = 'da'
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_original_language='+id_idioma
    pais = requests.get(url + '&page=' + str(n)).json()
    paginas = pais['total_pages']
    respais = pais['results']
    for pelis in respais:
        dinamarca.append(pelis['title'])
    time.sleep(2)

# 17. Alemania. de
print('alemania')
alemania = []
id_idioma = 'de'
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_original_language='+id_idioma
    pais = requests.get(url + '&page=' + str(n)).json()
    paginas = pais['total_pages']
    respais = pais['results']
    for pelis in respais:
        alemania.append(pelis['title'])
    time.sleep(2)

# 18. I Guerra Mundial. 2504
print('wwi')
wwi = []
id_keyword = 2504
n = 0
paginas = 500
while n < paginas:
    n += 1
    url = url_base+'&primary_release_date.lte=1920&with_keywords='+str(id_keyword)
    keyword = requests.get(url + '&page=' + str(n)).json()
    paginas = keyword['total_pages']
    reskeyword = keyword['results']
    for pelis in reskeyword:
        wwi.append(pelis['title'])
    time.sleep(2)

# 19. Todas. Se acota a 180 paginas para que solo devuelta 3600 peliculas, maximo de selecciones que admite Google Forms

todas = []
rango_inf = 1870
rango_sup = 1920
n = 0
paginas = 180
while n < paginas:
    n += 1
    print(n)
    url = url_base+'&primary_release_date.lte='+str(rango_sup)+'&primary_release_date.gte='+str(rango_inf)
    rangos = requests.get(url + '&page=' + str(n)).json()
    # paginas = rangos['total_pages']
    resrangos = rangos['results']
    for pelis in resrangos:
        todas.append(pelis['title'])
    time.sleep(2)

listacompleta = [griffith, feuillade, bauer, sjostrom, chaplin, weber, guy, western, terror, scifi, animation, primi1,
                 primi2, primi3, italia, dinamarca, alemania, wwi, todas]

df = pd.DataFrame(listacompleta).T
print(df)
columnas = ['Griffith','Feuillade','Bauer','Sjostrom','Chaplin','Weber','Guy','Western','Terror','Scifi','Animacion',
            'Origenes1','Origenes2','Origenes3','Italia','Dinamarca','Alemania','IGM','Todas']
df.columns = columnas
df.to_csv('quiniela_final_TFT1919.csv', sep=';', index=False)
