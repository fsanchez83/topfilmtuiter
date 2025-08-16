import csv
import yaml
from yaml.loader import SafeLoader
from bs4 import BeautifulSoup
import requests as rq
import os
import re
import time
import sys

## Para escrapear una lista solo es necesario introducir el list_id_cod (ScrapComments en archivo config)
## El codigo se encuentra buscando en el codigo fuente de la web data-report-url

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

list_id_cod = dataConfig['General']['ScrapComments']
id_lista = dataConfig['General']['id_lista']

csv_file_path = dataConfig['Resultados']['resultados_base'] + id_lista + '/Procesamiento/usuarios_comentarios.csv'

url = 'https://letterboxd.com/ajax/filmlist:'+str(list_id_cod)+'/comments/'

def get_users_and_lists(url, csv_file_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    request = rq.get(url, headers=headers)
    request.encoding = "utf-8"
    soup = BeautifulSoup(request.content, 'html.parser')

    # Find all comment list items
    comment_list_items = soup.find_all('li', class_='comment')

    # Extract and print the text of each comment
    comments_data_list = []
    for comment_item in comment_list_items:
        try:
            username = comment_item['data-person']
            comment_tag = comment_item.find('div', class_='comment-body')
            if comment_tag.find('a'):
                link_comentario = comment_tag.find('a')['href']
                link_comentario = link_comentario.replace("/detail", "")
            else:
                p_tag = comment_tag.find('p').get_text()
                match1 = re.search(r'boxd\.it/\w{5}', p_tag)
                match2 = re.search(r'letterboxd\.com/\S+', p_tag)

                if match1:
                    link_comentario = "https://" + match1.group(0)
                elif match2:
                    link_comentario = "https://" + match2.group(0)
                else:
                    link_comentario = None
            comments_data_list.append({'Participante': username, 'Lista': link_comentario})
        except:
            continue
    csv_columns = ['Participante', 'Lista']

    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(comments_data_list)





# Inicio del script
if __name__ == '__main__':

    # Almacena en un csv los usuarios y sus respectivas listas
    get_users_and_lists(url, csv_file_path)