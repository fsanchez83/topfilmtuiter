import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import sys
import yaml
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
    request = rq.get(url)
    request.encoding = "utf-8"
    response = rq.head(url, allow_redirects=True)
    url = response.url+'detail'
    request = rq.get(url)
    request.encoding = "utf-8"
    bs_page = BeautifulSoup(request.content, 'html.parser')
    lista_pelis = bs_page.find_all(class_="film-detail")

    lista_films = []
    posicion = 0
    for i in lista_pelis[:NmaxPelis]:
        lista_att = i.find(class_="headline-2 prettify")
        lista_numerada = lista_att.find(class_="list-number")
        url_peli = i.find('a')['href']
        if lista_numerada is None:
            posicion = posicion + 1
            titulo = lista_att.contents[0].get_text()
            if (len(lista_att.contents)<3):
                anio = 0
            else:
                anio = lista_att.contents[2].get_text()
        else:
            posicion, titulo_anio = lista_att.get_text().split(".", 1)
            titulo = lista_att.contents[1].get_text()
            if (len(lista_att.contents)<4):
                anio = 0
            else:
                anio = lista_att.contents[3].get_text()
        lista_films.append([posicion, titulo, anio, url_peli, url])
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
        except:
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
