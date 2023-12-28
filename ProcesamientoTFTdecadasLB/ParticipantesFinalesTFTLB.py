import csv
import yaml
from yaml.loader import SafeLoader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Para que funciones correctamente es posible que deba ejecutarse
# el chromedriver de selenium: https://chromedriver.chromium.org/downloads

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-certificate-errors-spki-list')
chrome_options.add_argument('--ignore-ssl-errors')


with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

list_id_cod = dataConfig['General']['ScrapComments']
id_lista = dataConfig['General']['id_lista']

csv_file_path = dataConfig['Resultados']['resultados_base'] + \
    id_lista + '/Procesamiento/usuarios_comentarios.csv'


# Guardamos la URL de la lista de inscripción
url = 'https://letterboxd.com/topfilmtuiter/list/inscripcion-top-filmtuiter-tft2010s/detail/'


def get_person_and_list(comment_item):
    # Verificar si la clase no contiene 'deleted' y prosigue la ejecución si es el caso
    if 'deleted' not in comment_item.get('class', ''):
        # Obtener y mostrar el nombre del usuario
        name_person_value_link = comment_item.find(
            class_='name').find('a')
        if name_person_value_link:
            name_person_value = name_person_value_link.get(
                'href').replace("/", "")

        # Encontrar el enlace dentro del párrafo (<p>) del comentario
        list_link = comment_item.find('p').find('a')

        # Obtener y mostrar el atributo href del enlace
        if list_link:
            list_value = list_link.get('href')
        # print(f'Usuario: {name_person_value}, lista: {list_value}')
        return [name_person_value, list_value]

    # Si no se cumple alguna condición, devolver una lista vacía o None
    return []


def get_comments_in_page(csv_writer, driver):
    # Crear un conjunto para almacenar usuarios y listas y evitar duplicados y vacíos
    user_list_set = set()
    # Esperar a que aparezca el enlace "Load Previous" y hacer clic en él
    show_previous_link_locator = (By.ID, 'load-previous-comments')
    while True:
        try:
            WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable(show_previous_link_locator)).click()

            # Esperar un momento para que se carguen los comentarios
            time.sleep(2)

        except TimeoutException:
            # Si se produce un TimeoutException, significa que el botón ya no está presente
            # Obtener el contenido de la página después de cargarla dinámicamente
            page_content = driver.page_source

            # Utilizar BeautifulSoup para analizar el contenido
            bs_page = BeautifulSoup(page_content, 'html.parser')

            # Ahora puedes buscar los comentarios y acceder a los atributos que necesitas
            comment_list = bs_page.find(
                'ul', class_='comment-list js-comment-list')

            if comment_list:
                for comment_item in comment_list.find_all('li', class_='comment'):
                    person_and_list = get_person_and_list(comment_item)
                    if person_and_list and tuple(person_and_list) not in user_list_set:
                        csv_writer.writerow(person_and_list)
                        user_list_set.add(tuple(person_and_list))
            break


def close_cookies_popup(driver):
    # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
    driver.implicitly_wait(10)

    # Esperar a que aparezca el pop-up de consentimiento y hacer clic en el botón "Consent"
    consent_button_locator = (
        By.CLASS_NAME, 'fc-button.fc-cta-consent.fc-primary-button')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(consent_button_locator)).click()

    # Hace scroll hacia abajo para que los banners no interfieran
    driver.execute_script("window.scrollBy(0, 400);")


def get_users_and_lists(url, csv_file_path):

   # Configurar el navegador de Selenium (asegúrate de tener el controlador adecuado instalado)
    driver = webdriver.Chrome(options=chrome_options)

    # Cargar la página
    driver.get(url)

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Crear un escritor CSV
            csv_writer = csv.writer(csv_file)

            # Escribir encabezados
            csv_writer.writerow(['Participante', 'Lista'])

            close_cookies_popup(driver)

            get_comments_in_page(csv_writer, driver)

            print(
                f'Los datos se han guardado en el archivo CSV: {csv_file_path}')

    except Exception as e:
        print(
            f'Ha ocurrido un error al intentar leer la lista de usuarios desde Letterboxd: {repr(e)}')

    finally:
        # Cerrar el navegador al finalizar
        driver.quit()


# Inicio del script
if __name__ == '__main__':

    # Almacena en un csv los usuarios y sus respectivas listas
    get_users_and_lists(url, csv_file_path)
