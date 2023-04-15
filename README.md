# topfilmtuiter

Conjunto de scripts utilizados para implementar la iniciativa "Top Filmtuiter", cuyas distintas ediciones pueden leerse en [este enlace](https://twitter.com/topfilmtuiter/status/1643696016288280580) de la cuenta de Twitter [@topfilmtuiter](https://twitter.com/topfilmtuiter). Los resultados están publicados en [este perfil de Letterboxd](https://letterboxd.com/topfilmtuiter/lists/) y en [este informe de Power BI](https://app.powerbi.com/view?r=eyJrIjoiODhiOWQwMzUtNTVhYy00ZWYxLTk0MDEtNDRmNTQ1YWJjODk3IiwidCI6ImFmM2E0NDRiLTcwMWItNGVkNi05YzhlLTg0ZGE5MmQ0Zjk2OSIsImMiOjl9).

El conjunto del proyecto puede estructurarse de la siguiente manera, correspondiendo cada apartado a una carpeta:

1. Selección de los participantes potenciales (ParticipantesTopFilmTuiter)
2. Procesamiento de resultados (Procesamiento)
    1. Recolección de usuarios participantes.
    2. Procesamiento de las listas.
    3. Enriquecimiento de los datos.
    4. TopFilmTinder.
3. Resultados de cada edición (Resultados)
4. Explotación de los datos con Power BI (PBI)
5. Actividad paralela: quiniela (Quiniela)

Para las credenciales necesarias para las distintas APIs se emplean las credenciales del fichero yaml de configuración secrets.cfg. Se deja en el repositorio raíz una plantilla para ayudar a completarlo. También se incluye un yaml con parámetros de configuración que se deberá modificar para cada lista. Se mantiene como ejemplo el utilizado para la edición TFT1919.

## 1. Selección de los participantes potenciales

Se emplea el script *PotencialesParticipantes.py*. Es necesario introducir las credenciales personales de desarrollador para la API de Twitter. El script genera un csv con todas las personas seguidas por los usuarios introducidos en la lista *user_ref*. Se genera un csv con dos campos: el primero con el nombre del usuario seguido y el segundo con el número de usuarios que lo siguen. El script permite una realimentación cíclica; es decir, se puede introducir como entrada el csv de salida, resultando de esta manera todos los usuarios seguidos por los usuarios del csv. Para aplicar esto (entrada de datos por csv en vez de por array) es necesario descomentar el bloque indicado en el código a tal efecto.

### Observaciones
Hay que tener en cuenta que no se computarán las cuentas candado cuando estas no sean seguidas por el usuario asociados a las credenciales de la API utilizadas en la ejecución del programa. En ese caso, estos usuarios se ignoran en el bucle.  

Se incluye también, como ayuda complementaria, el script *MezclaListas.py*. Este script permite introducir como entrada dos csv generados por el script *PotencialesParticipantes.csv* en diferentes momentos. El resultado es un csv con una nueva columna que indica, para cada usuario, si aparecía solo en la primera lista, solo en la segunda o en ambas.

## 2. Procesamiento de resultados

Para recopilar y enriquecer los resultados es necesario seguir 3 pasos: recoger los nombres de usuario de Letterboxd de los participantes como respuesta a un tweet dado; scrapear las listas de Letterboxd de esos usuarios, asignarles la puntuación en función de la posición y generar las listas de resultados; enriquecer los resultados añadiendo, en cada película, información complementaria procedente de *The Movie DataBase*.

Se ha generado un script de pipeline (*pipeline completo.py*) que, simplemente, ejecuta secuencialmente estos tres scripts.

### 2.1. Recolección de usuarios participantes finales.

A partir de un tweet, se recogen las respuestas y se añaden a un txt, donde cada línea es una respuesta. Utiliza la API clásica de Twitter, por lo que hay que introducir para la autenticación los valores de consumer_key, consumer_secret, access_token y access_token_secret. Hay que recordar que, con un usuario gratuito de la API, Twitter solo devuelve las respuestas de los últimos 7 días, por lo que, si el periodo de inscripción dura más de 7 días, hay que ejecutar el script al menos una vez cada semana. El script es idempotente e incremental, por lo que va añadiendo los usuarios nuevos y no hay problema por ejecutarlo varias veces.

El script, *ParticipantesFinalesTFT.py*, va añadiendo a un archivo txt (*usuarios.txt*) dado las nuevas respuestas. En caso de que las respuestas tengan varias palabras, la segunda se toma como nombre de la lista, sustituyendo para dicho usuario ese nombre por el id de la lista estándar que se emplea por defecto. Las demás palabras de los tweets se eliminan. Además, se borran los posibles duplicados que aparezcan.

### 2.2. Procesamiento de las listas.

Se realiza con el script *Top_FilmTuiter.py*.

Se recopilan en un dataframe, conservando su orden (ya sea o no una lista ordenada), todas las películas incluidas en las listas de Letterboxd de los usuarios de *usuariosIDLISTA.csv* con el nombre definido como id_lista en el fichero de configuración.
Según el orden de cada película en cada lista se le asigna una puntuación (definida en el propio main.py) y se recopila y suma en una lista final. El programa scrapea la URL en Letterboxd de cada película de la lista, incorporándolo en los ficheros de salida.

#### Entradas
El programa no tiene parámetros de entrada. Es suficiente con ejecutar el main.py.

El programa utiliza como datos de entrada el contenido de un csv:
- usuariosIDLISTA.csv. Listado de usuarios participantes en la encuesta y nombre de su lista (vacío si es el id estándar)

#### Salidas
Se generan como salida dos archivos csv:
- Lista_votaciones_IDLISTA.csv. Listado con todas las listas que se computan concatenadas, manteniendo la posición en cada lista individual y la puntuación correspondiente.
- Lista_votaciones_stats_lb.csv. Lista agregada, sumando los puntos de todas las listas computadas y ordenada de mayor a menor puntuación total. Este csv se puede importar en Letterboxd como una lista. La puntuación total de la película se guarda en la review.
- Lista_votaciones_stats_IDLISTA.csv. Lista agregada, sumando los puntos de todas las listas computadas y ordenada de mayor a menor puntuación total sin formateo para importar en Letterboxd, pero más usable para utilizar en el siguiente paso. Incluye una columna con la URI diferencial en Letterboxd de cada película.


### 2.3. Enriquecimiento de los datos.

Se realiza con el script *createDatasetTFT.py*.

Necesita tener una cuenta para utilizar la [API de TMDB](https://developers.themoviedb.org/3/getting-started/introduction), que se puede solicitar gratuitamente. Por ello, en el fichero de configuración debe introducirse el valor de la API_KEY. 

El programa coge la lista de películas generada en el paso anterior (*Lista_votaciones_stats_IDLISTA.csv*), navega a su URL en Letterboxd y mediante scraping obtiene el ID de la película en TMDB (y tipo). Después, mediante llamadas a la API de TMDB, se busca esas películas y se crea un dataset en el que se incluye, a cada película de la lista, los siguientes atributos: ['Votos', "url_peli", "Id_peli", "Titulo", "Popularidad", 'Rating', 'Fecha', 'Duracion', 'Pais', 'Idioma', 'Presupuesto', 'Ganancia', 'Generos', 'Director', 'Genero_dir', 'Casting', 'Guion', 'Montaje', 'DOP', 'Resumen'].

Aunque sea muy extraño, puede ocurrir que en alguna ficha de Letterboxd sea erróneo el id de la película en TMDB. Para corregir esos casos, se posibilita introducir manualmente el id de películas específicas. Esto se hace mediante el archivo de texto *filmid_whitelist*.

En función del tipo de película (movie o tv) se obtienen unos u otros datos de la API, llamando a funciones diferentes, pero el resultado se guarda en un modelo de lista común. Estas listas (una por película) se incorporan al dataset. Finalmente, este dataset se guarda en el archivo *dataset_ID_LISTA.csv*. Durante el proceso, que puede tardar unos minutos, se indican por pantalla todos los casos en los que no se produzca un match exacto en cine, que es el caso mayoritario en este caso. El programa, antes de iniciar su flujo, carga el csv resultante en caso de que exista. De esa manera, solo se hará el scraping de las películas que falten en el fichero. De esta manera, cada ejecución es incremental, incorporando las películas que no estuvieran previamente, e idempotente, ya que el resultado de ejecutarlo N veces es igual a ejecutarlo solo una vez en el instante de ejecución N.

Este archivo, junto con el *Lista_votaciones.csv* generado en el paso 2.2, se utiliza como pase para el pbix que genera todas las estadísticas en Power BI.

Se incluyen también estos archivos, además del pbix, en la carpeta de Resultados. También se incluye un fichero llamado directoras.txt, que se ha generado manualmente y se utiliza, en el informe de Power BI, para poder resaltar las directoras del conjunto de datos.

### 2.4. TopFilmTinder.

Utiliza el fichero Lista_votaciones_IDLISTA.csv para obtener una matriz con todos los usuarios, ítems y puntos a cada ítem en la lista. Sobre esto, utilizando la librería de sistemas de recomendación Surprise, se generan dos modelos, uno para generar los crushes y otro las recomendaciones de películas (sugerencias de la comunidad para que un usuario hubiera incluido otras películas en su lista).

#### Crushes

Se obtiene la medida de afinidad de cada usuario contra todos los demás. La métrica de afinidad se compone del número de elecciones comunes a las listas sumado a una métrica de similaridad (que como máximo supone un +-1) para considerar el orden de estas. Esta métrica de similaridad se ha obtenido mediante una correlación de Pearson de los puntos concedidos a cada película, centrado en baselines y con un pequeño coeficiente de regularización para minimizar el sobreajuste (ya que hay pocos datos). Se genera un fichero resultante (lista_vecinos_ID_LISTA.csv) con los vecindarios y medidas de afinidad de cada usuario.

#### Sugerencias

Se obtiene una tabla de sugerencias personalizadas que hace la comunidad a cada participante sobre películas no incluidas en su lista, hallando una estimación de puntuación de 1 a 5. Para esta métrica se ha empleado un sencillo filtrado colaborativo (es decir, no se consideran las características de las películas, que sería lo más interesante pero queda para una futura versión) aplicando una factorización SVD optimizada en 6 epochs con un algoritmo SDG. Se genera un fichero resultante (lista_recos_ID_LISTA.csv) con las recomendaciones para cada usuario.

## 3. Resultados

Directorio con el árbol de los ficheros resultantes en cada lista.

## 4. Explotación de los datos con Power BI (PBI)

Se incluye el fichero pbix, preparado ya para procesar N listas. Los datos necesarios están incluidos en la propia carpeta (se guardan aquí en paralelo durante el procesado).

## 5. Quiniela

Explicado en el siguiente hilo de Twitter: https://twitter.com/topfilmtuiter/status/1642478490657210370
