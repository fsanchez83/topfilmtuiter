import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import re
import random
import time
import sys
from yaml.loader import SafeLoader

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']

def scrape_films_watched(user, decade=None, es_decada=None):
    # Scrape total films watched
    user_url = f"https://letterboxd.com/{user}"
    delay = random.uniform(1, 2)  # entre 1 y 2 segundos
    time.sleep(delay)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    delay = random.uniform(1.5, 3.0)  # entre 1.5 y 3 segundos
    time.sleep(delay)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(user_url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch {user_url}, status code: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    total_films_tag = soup.find('h4', class_='profile-statistic statistic')
    if total_films_tag is None:
        print(f"Error: Could not find total films watched on {user}'s profile page.")
        return None, None

    total_films_watched = total_films_tag.find('span', class_='value').text.replace(',','')

    total_films_watched = int(total_films_watched)

    # Scrape films watched in the given decade
    films_in_decade = None
    if decade:
        decade_url = f"https://letterboxd.com/{user}/films/decade/{decade}s/"

        response = requests.get(decade_url)
        if response.status_code != 200:
            print(
                f"Error: Failed to fetch {decade_url}, status code: {response.status_code}")
            return total_films_watched, None

        soup = BeautifulSoup(response.text, 'html.parser')
        decade_films_tag = soup.find('p', class_='ui-block-heading')
        if decade_films_tag:
            # Extract text and search for the pattern
            text_content = decade_films_tag.get_text(strip=True)
            text_content = text_content.replace(',', '')
            match = re.search(r'watched (\d+) films', text_content)
            if match:
                films_in_decade = int(match.group(1).replace(',', ''))
            else:
                print(
                    f"Error: Could not extract films watched in the {decade}s for {user}.")

    return total_films_watched, films_in_decade


def process_users(input_csv, output_csv, decada, es_decada):
    # Read the input CSV
    try:
        users_df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return

    if 'Participante' not in users_df.columns:
        print("Error: The input CSV does not have a 'Participante' column.")
        return

    # Prepare results
    results = []
    for user in users_df['Participante']:
        print(f"Processing user: {user}")
        try:
            total, decade_count = scrape_films_watched(user, decada, es_decada)
            results.append({
                'Participante': user,
                'Peliculas_totales': total,
                'Peliculas_decada': decade_count
            })
        except Exception as e:
            print(f"Error processing user {user}: {e}")
            results.append({
                'Participante': user,
                'Peliculas_totales': None,
                'Peliculas_decada': None
            })

    # Write results to the output CSV
    results_df = pd.DataFrame(results)
    try:
        results_df.to_csv(output_csv, index=False)
        print(f"Results saved to {output_csv}")
    except Exception as e:
        print(f"Error writing output CSV: {e}")


# Example usage
if __name__ == "__main__":
    input_csv = dataConfig['Resultados'][
                        'resultados_base'] + id_lista + '/Procesamiento/usuarios_comentarios.csv'

    output_csv_res = dataConfig['Resultados'][
                        'resultados_base'] + id_lista + \
                 '/Procesamiento/datos_usuarios_'+id_lista+'.csv'

    output_csv = dataConfig['Resultados'][
                         'base_pbi'] + 'datos_usuarios/datos_usuarios_' + id_lista\
                     + '.csv'
    decada = dataConfig['Decadas']['anno_ini']

    es_decada = dataConfig['Decadas']['es_decada']
    process_users(input_csv, output_csv, decada, es_decada)
