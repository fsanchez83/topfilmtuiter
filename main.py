import pandas as pd
import requests as rq
from bs4 import BeautifulSoup

# Test con las siguientes listas:
# https://letterboxd.com/arrival/list/favoritas/
# https://letterboxd.com/victorjugo12/list/favoritas/
# https://letterboxd.com/pendejis/list/favoritas/


def get_films(usuario, nombre):
    url = 'https://letterboxd.com/' + usuario + '/list/' + nombre + '/detail'
    request = rq.get(url)
    request.encoding = "utf-8"
    bs_page = BeautifulSoup(request.content, 'html.parser')
    lista_pelis = bs_page.find_all(class_="film-detail")

    lista_films = []
    posicion = 0
    for i in lista_pelis:
        lista_att = i.find(class_="headline-2 prettify")
        lista_numerada = lista_att.find(class_="list-number")
        if lista_numerada is None:
            posicion = posicion + 1
            titulo_anio = lista_att.get_text()
        else:
            posicion, titulo_anio = lista_att.get_text().split(".", 1)

        titulo = titulo_anio[:-4]
        anio = titulo_anio[-4:]
        lista_films.append([posicion, titulo, anio])

    return lista_films


def calcula_puntos(pos):
    # ASIGNAR PUNTOS SEGUN EL ORDEN
    # 1ª: 5 puntos,
    # 2ª - 4ª: 4 pts
    # 5 - 9: 3  pts
    # 10 - 16: 2 pts
    # 17 - 25: 1 punto

    pos = int(pos)
    if pos == 1:
        pts = 5
    elif pos < 5:
        pts = 4
    elif pos < 10:
        pts = 3
    elif pos < 17:
        pts = 2
    elif pos < 26:
        pts = 1
    else:
        pts = 0
    return pts


# Inicio del script
if __name__ == '__main__':
    nombre_lista = open("nombre_lista.txt", "r").read()

    listausuarios = open("usuarios.txt", "r")
    usuarios = listausuarios.read().splitlines()
    listausuarios.close()

    lista_global = []
    contador = 0
    for nombre_usr in usuarios:
        lista_films = get_films(nombre_usr, nombre_lista)
        if len(lista_films) > 0:
            contador = contador + 1
        lista_global.append(lista_films)
    print('Número de participantes: ', contador)
    flat_list = [item for sublist in lista_global for item in sublist]
    df_lista = pd.DataFrame(flat_list, columns=['Pos', 'Titulo', 'Anio'])
    df_lista['Titulo'] = df_lista['Titulo'].str.strip()
    df_lista['Puntos'] = df_lista.apply(lambda row: calcula_puntos(row['Pos']), axis=1)
    df_lista.to_csv('Lista_votaciones.csv')
    resultado_final = df_lista.groupby(['Titulo', 'Anio']).agg({'Puntos': 'sum'}).sort_values('Puntos', ascending=False)
    resultado_final.to_csv('Lista_votaciones_stats.csv')
