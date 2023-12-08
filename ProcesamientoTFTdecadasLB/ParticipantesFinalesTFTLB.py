import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Para que funciones correctamente es posible que deba ejecutarse
# el chromedriver de selenium: https://chromedriver.chromium.org/downloads


def get_users_and_lists():

    # Crear un archivo CSV
    csv_file_path = './Resultados/ResultadosTFTDecadasLB/usuarios_comentarios.csv'

    # Guardamos la URL de la lista de inscripción
    url = 'https://letterboxd.com/topfilmtuiter/list/inscripcion-top-filmtuiter-tft2010s/detail/'

   # Configurar el navegador de Selenium (asegúrate de tener el controlador adecuado instalado)
    driver = webdriver.Chrome()

    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            # Crear un escritor CSV
            csv_writer = csv.writer(csv_file)

            # Escribir encabezados
            csv_writer.writerow(['Participante', 'Lista'])
            # Cargar la página
            driver.get(url)

            # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
            driver.implicitly_wait(10)

            # Esperar a que aparezca el pop-up de consentimiento y hacer clic en el botón "Consent"
            consent_button_locator = (
                By.CLASS_NAME, 'fc-button.fc-cta-consent.fc-primary-button')
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(consent_button_locator)).click()

            # Esperar a que aparezca el enlace "Show all" y hacer clic en él
            show_all_link_locator = (By.ID, 'load-all-comments')
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(show_all_link_locator)).click()

            # Esperar un momento para que se carguen los comentarios
            time.sleep(2)

            # Obtener el contenido de la página después de cargarla dinámicamente
            page_content = driver.page_source

            # Utilizar BeautifulSoup para analizar el contenido
            bs_page = BeautifulSoup(page_content, 'html.parser')

            # Ahora puedes buscar los comentarios y acceder a los atributos que necesitas
            comment_list = bs_page.find(
                'ul', class_='comment-list js-comment-list')

            if comment_list:
                for comment_item in comment_list.find_all('li', class_='comment'):
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
                        csv_writer.writerow([name_person_value, list_value])
                        # print('Participante: ' + str(data_person_value) +
                        #      ', lista: ' + str(href_value))
                print(
                    f'Los datos se han guardado en el archivo CSV: {csv_file_path}')

            else:
                print('No se encontró la lista de comentarios en la página.')

    except:
        print('Ha ocurrido un error al intentar leer la lista de usuarios desde Letterboxd')

    finally:
        # Cerrar el navegador al finalizar
        driver.quit()


# Inicio del script
if __name__ == '__main__':

    # Almacena en un csv los usuarios y sus respectivas listas
    get_users_and_lists()
