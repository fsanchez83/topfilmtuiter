import csv
import yaml
from yaml.loader import SafeLoader
from bs4 import BeautifulSoup
import requests as rq
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

    request = rq.get(url)
    request.encoding = "utf-8"
    soup = BeautifulSoup(request.content, 'html.parser')

    # Find all comment list items
    comment_list_items = soup.find_all('li', class_='comment')

    # Extract and print the text of each comment
    comments_data_list = []
    for comment_item in comment_list_items:
        try:
            username = comment_item['data-person']
            link_comentario = comment_item.find('div', class_='comment-body').find('a')['href']
            comments_data_list.append({'Participante': username, 'Lista': link_comentario})
        except:
            continue
    csv_columns = ['Participante', 'Lista']

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(comments_data_list)





# Inicio del script
if __name__ == '__main__':

    # Almacena en un csv los usuarios y sus respectivas listas
    get_users_and_lists(url, csv_file_path)
