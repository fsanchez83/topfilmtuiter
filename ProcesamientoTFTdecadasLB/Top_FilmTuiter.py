import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import sys
import yaml
import random
import time
from yaml.loader import SafeLoader

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']

lista_completa = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'_bruto.csv'
lista_completa_pbi = dataConfig['Resultados']['base_pbi']+'listas_votaciones/Lista_votaciones_'+id_lista+'_bruto.csv'
lista_stats_base = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_'+id_lista+'_bruto.csv'
lista_stats_base_lb = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_stats_lb_bruto.csv'
lista_usrs = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/usuarios_comentarios.csv'

def get_films(url_lista, NmaxPelis):
    #url = 'https://letterboxd.com/' + usuario + '/list/' + nombre + '/detail'
    url = url_lista
    ## URL para pruebas previas al TFTdescubrimientos
    #url = 'https://letterboxd.com/danielquinn/list/tft1919/detail/'
    delay = random.uniform(1.5, 3.0)  # entre 1.5 y 3 segundos
    time.sleep(delay)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    request = rq.get(url, allow_redirects=True, headers=headers)
    #request.encoding = "utf-8"
    #delay = random.uniform(1.5, 3.0)  # entre 1.5 y 3 segundos
    #time.sleep(delay)
    #response = rq.head(url, allow_redirects=True, headers=headers)
    url = request.url+'detail'
    print(url)
    delay = random.uniform(1.5, 3.0)  # entre 1.5 y 3 segundos
    time.sleep(delay)
    request = rq.get(url, headers=headers)
    request.encoding = "utf-8"
    bs_page = BeautifulSoup(request.content, 'html.parser')
    lista_pelis = bs_page.find_all(class_="listitem js-listitem")
    lista_films = []
    posicion = 0
    for i in lista_pelis[:NmaxPelis]:
        posicion = posicion + 1
        nompre_url_html = i.find(class_="name -primary prettify")
        url_peli = nompre_url_html.find('a')['href']
        titulo = nompre_url_html.contents[0].get_text(strip=True)
        anio = (anio_html.find('a').get_text(strip=True)
                if (anio_html := i.find(class_="releasedate")) and anio_html.find('a')
                else None)
        lista_films.append([posicion, titulo, anio, url_peli, url])
    print(lista_films)
    return lista_films, url


def calcula_puntos(pos):
    # ASIGNAR PUNTOS SEGUN EL ORDEN
    # 1ª: 6 puntos,
    # 2ª - 5ª: 5 pts
    # 6 - 10: 4  pts
    # 11 - 15: 3 pts
    # 16 - 20: 2 pts
    # 21 - 25: 1 punto

    pos = int(pos)
    if pos == 1:
        pts = 6
    elif pos < 6:
        pts = 5
    elif pos < 11:
        pts = 4
    elif pos < 16:
        pts = 3
    elif pos < 21:
        pts = 2
    elif pos < 26:
        pts = 1
    else:
        pts = 0
    return pts


# Inicio del script
if __name__ == '__main__':

    df_usuarios = pd.read_csv(lista_usrs).drop_duplicates()
    print(df_usuarios)

    sin_lista = []
    lista_global = []
    contador = 0

    for i in range(len(df_usuarios)):

        print(df_usuarios.iloc[i]['Participante'])
        try:
            lista_films,url = get_films(df_usuarios.iloc[i]['Lista'], 25)

            if len(lista_films) > 0:
                contador += 1
                #print(url)
            else:
                sin_lista.append(df_usuarios.iloc[i]['Usuarios'])
            lista_global.append(lista_films)
        except Exception as e:
            print(f"Error: {e}")
            print("Lista no válida")
            continue
    print('Número de participantes: ', contador)
    print('Faltan: ', sin_lista)
    flat_list = [item for sublist in lista_global for item in sublist]
    df_lista = pd.DataFrame(flat_list, columns=['Pos', 'Titulo', 'Anio', 'url_peli', 'url'])
    df_lista['Titulo'] = df_lista['Titulo'].str.strip()
    df_lista['Puntos'] = df_lista.apply(lambda row: calcula_puntos(row['Pos']), axis=1)
    df_lista.to_csv(lista_completa)
    #df_lista.to_csv(lista_completa_pbi)

    resultado_final = df_lista.groupby(['Titulo', 'Anio', 'url_peli']).agg({'Puntos': 'sum', 'Titulo': 'count'}).rename(
        columns={"Puntos": "Puntos", "Titulo": "Menciones"}).sort_values(
        ['Puntos', 'Menciones'], ascending=[False, False])

    resultado_final_lb = resultado_final.reset_index(level='url_peli')
    resultado_final_lb = resultado_final_lb.astype({'Puntos': 'str', 'Menciones': 'str'})
    resultado_final_lb["Review"] = resultado_final_lb["Puntos"] + " puntos con " + resultado_final_lb[
        "Menciones"] + " menciones"
    resultado_final_lb = resultado_final_lb.rename_axis(index={'Titulo': 'Title', "Anio": "Year"})
    resultado_final_lb = resultado_final_lb.drop(['url_peli', 'Puntos', 'Menciones'], axis=1)
    resultado_final_lb.to_csv(lista_stats_base_lb)

    resultado_final = resultado_final.rename(columns={"Puntos": "Review"})
    resultado_final = resultado_final.rename_axis(index={'Titulo': 'Title', "Anio": "Year"})
    resultado_final = resultado_final.drop(['Menciones'], axis=1)
    resultado_final.to_csv(lista_stats_base)
    print(resultado_final)
