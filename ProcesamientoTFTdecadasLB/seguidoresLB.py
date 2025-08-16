import pandas as pd
import yaml
from yaml.loader import SafeLoader
import requests
import random
import time
from bs4 import BeautifulSoup

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']
csv_file_path = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/usuarios_comentarios.csv'

df_usuarios = pd.read_csv(csv_file_path)

# Función para obtener followers o followings de una página
def obtener_personas_pagina(base_url, usuario, accion, pagina):
    url = f'{base_url}{usuario}/{accion}/page/{pagina}/'
    delay = random.uniform(1.5, 3.0)  # entre 1.5 y 3 segundos
    time.sleep(delay)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parsear el HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Encontrar todos los elementos con clase "follow-button-wrapper js-follow-button-wrapper" que contienen los nombres
        personas = soup.find_all('div', class_='follow-button-wrapper js-follow-button-wrapper')

        # Extraer el nombre de cada persona (follower o following) y añadirlo a una lista
        nombres_personas = [persona['data-username'] for persona in personas]

        return nombres_personas
    else:
        print(f"Error al acceder a la página {pagina} para el usuario {usuario}. Código de estado: {response.status_code}")
        return []

# Función para iterar por todas las páginas de followers o followings de un usuario
def obtener_todas_las_personas(base_url, usuario, accion):
    pagina = 1
    todas_personas = []

    while True:
        print(f"Scrapeando {accion} de {usuario}, página {pagina}...")
        personas_pagina = obtener_personas_pagina(base_url, usuario, accion, pagina)

        # Si no hay personas en la página, asumimos que hemos llegado al final
        if not personas_pagina:
            break

        # Añadir las personas de esta página a la lista total
        todas_personas.extend(personas_pagina)

        # Avanzar a la siguiente página
        pagina += 1

    return todas_personas

# URL base para followers y followings
url_base = 'https://letterboxd.com/'

# Listas para almacenar los datos de los followers y followings de todos los usuarios
followers_data = []
followings_data = []

# Iterar por cada usuario en el dataframe
for usuario in df_usuarios['Participante']:
    # Obtener followers de cada usuario y almacenarlos en la lista con su correspondiente usuario
    followers_usuario = obtener_todas_las_personas(url_base, usuario,'followers')
    for follower in followers_usuario:
        followers_data.append((usuario, follower))  # Guardamos en formato (usuario, follower)

    # Obtener followings de cada usuario y almacenarlos en la lista con su correspondiente usuario
    followings_usuario = obtener_todas_las_personas(url_base, usuario,'following')
    for following in followings_usuario:
        followings_data.append((usuario, following))  # Guardamos en formato (usuario, following)

# Crear dataframes a partir de las listas
df_followers = pd.DataFrame(followers_data, columns=['Usuario', 'Follower'])
df_followings = pd.DataFrame(followings_data, columns=['Usuario', 'Following'])

# Mostrar los dataframes resultantes
print("DataFrame de Followers:")
print(df_followers)

print("\nDataFrame de Followings:")
print(df_followings)

csv_followers_path = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followers.csv'

csv_followings_path = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followings.csv'

df_followers.to_csv(csv_followers_path, index=False)
df_followings.to_csv(csv_followings_path, index=False)