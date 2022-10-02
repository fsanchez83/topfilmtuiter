# topfilmtuiter

Conjunto de scripts utilizados para implementar la iniciativa "Top Filmtuiter", cuyas normas pueden leerse en [este enlace](https://twitter.com/topfilmtuiter/status/1515757646430801927) de la cuenta de Twitter [@topfilmtuiter](https://twitter.com/topfilmtuiter). Los resultados están publicados en [esta lista de Letterboxd](https://letterboxd.com/topfilmtuiter/list/resultados-finales-top-filmtuiter/) y en [este informe de Power BI](https://app.powerbi.com/view?r=eyJrIjoiODhiOWQwMzUtNTVhYy00ZWYxLTk0MDEtNDRmNTQ1YWJjODk3IiwidCI6ImFmM2E0NDRiLTcwMWItNGVkNi05YzhlLTg0ZGE5MmQ0Zjk2OSIsImMiOjl9).

El conjunto de scripts puede estructurarse de la siguiente manera:

1. Selección de los participantes potenciales.
2. Procesamiento de resultados.
    1. Recolección de usuarios participantes.
    2. Procesamiento de las listas.
    3. Enriquecimiento de los datos.

## 1. Selección de los participantes potenciales

Se emplea el script *PotencialesParticipantes.csv*. Es necesario introducir un bearer_token para poder utilizar la API de Twitter. El script genera un csv con todas las personas seguidas por los usuarios introducidos en la lista *user_ref*. Se genera un csv con dos campos: el primero con el nombre del usuario seguido y el segundo con el número de usuarios que lo siguen. El script permite una realimentación cíclica; es decir, se puede introducir como entrada el csv de salida, resultando de esta manera todos los usuarios seguidos por los usuarios del csv. Para aplicar esto (entrada de datos por csv en vez de por array) es necesario descomentar el bloque indicado en el código a tal efecto.

### Observaciones
Hay que tener en cuenta que no se computarán las cuentas candado cuando estas no sean seguidas por el usuario con las credenciales para utilizar el API. En ese caso, estos usuarios se ignoran en el bucle.  

Se incluye también, como ayuda complementaria, el script *MezclaListas.py*. Este script permite introducir como entrada dos csv generados por el script *PotencialesParticipantes.csv* en diferentes momentos. El resultado es un csv con una nueva columna que indica, para cada usuario, si aparecía solo en la primera lista, solo en la segunda o en ambas.

## 2. Procesamiento de resultados

Para recopilar y enriquecer los resultados es necesario seguir 3 pasos: recoger los nombres de usuario de Letterboxd de los participantes como respuesta a un tweet dado; scrapear las listas de Letterboxd de esos usuarios, asignarles la puntuación en función de la posición y generar las listas de resultados; enriquecer los resultados añadiendo, en cada película, información complementaria procedente de *The Movie DataBase*.

Se ha generado un script de pipeline (*pipeline completo.py*) que, simplemente, ejecuta secuencialmente estos tres scripts.

### 2.1. Recolección de usuarios participantes finales.

A partir de un tweet, se recogen las respuestas y se añaden a un txt, donde cada línea es una respuesta. Utiliza la API clásica de Twitter, por lo que hay que introducir para la autenticación los valores de consumer_key, consumer_secret, access_token y access_token_secret. Hay que recordar que, con un usuario gratuito de la API, Twitter solo devuelve las respuestas de los últimos 7 días, por lo que, en el caso de Top Filmtuiter, hubo que ejecutar el script al menos una vez cada semana durante el mes que estuvo vigente la inscripción.

El script, *ParticipantesFinalesTFT.py*, va añadiendo a un archivo txt (*usuarios.txt*) dado las nuevas respuestas. En caso de que las respuestas tengan varias palabras, se queda solo con la primera. Además, se borran los posibles duplicados que aparezcan.

### 2.2. Procesamiento de las listas.

Se realiza con el script *Top_FilmTuiter.py*.

Se recopilan en un dataframe, conservando su orden (ya sea o no una lista ordenada), todas las películas incluidas en las listas de Letterboxd de los usuarios de *usuarios.txt* con el nombre definido en *nombre_lista.txt*.
Según el orden de cada película en cada lista se le asigna una puntuación (definida en el propio main.py) y se recopila y suma en una lista final.

#### Entradas
El programa no tiene parámetros de entrada. Es suficiente con ejecutar el main.py.

El programa utiliza como datos de entrada el contenido de dos archivos de texto:
- usuarios.txt. Listado de usuarios participantes en la encuesta
- nombre_lista.txt. Nombre de la lista de Letterboxd de la que se recopilarán los datos. Es decir, las listas de todos los usuarios deben tener el mismo nombre.

#### Salidas
Se generan como salida dos archivos csv:
- Lista_votaciones.csv. Listado con todas las listas que se computan concatenadas, manteniendo la posición en cada lista individual y la puntuación correspondiente.
- Lista_votaciones_stats.csv. Lista agregada, sumando los puntos de todas las listas computadas y ordenada de mayor a menor puntuación total. Este csv se puede importar en Letterboxd como una lista. La puntuación total de la película se guarda en la review.

#### Observaciones
Para evitar errores en el nombre de las listas de Letterboxd que ponen los usuarios, se incluyó en el código distintas variaciones del nombre principal dentro del bucle que comprueba la existencia de la lista en cada usuario de Letterboxd. Aunque lo ideal sería tener esto en un archivo de configuración aparte, por la premura de tiempo se incluyeron estas variaciones directamente en el código. En la próxima evolución sería recomendable sacar estar parte a un archivo aparte.

### 2.3. Enriquecimiento de los datos.

Se realiza con el script *createDatasetTFT.py*.

Necesita tener una cuenta para utilizar la [API de TMDB](https://developers.themoviedb.org/3/getting-started/introduction), que se puede solicitar gratuitamente. Por ello, al principio del script hay que introducir el valor de tmdb.API_KEY. 

El programa coge la lista de películas generada en el paso anterior (*Lista_votaciones_stats.csv*) y, mediante llamadas a la API de TMDB, se busca esas películas y se crea un dataset en el que se incluye, a cada película de la lista, los siguientes atributos: ['Votos', 'Id_peli', 'Titulo', 'Popularidad', 'Rating', 'Fecha', 'Duracion', 'Pais', 'Idioma', 'Presupuesto', 'Ganancia', 'Generos', 'Director', 'Casting', 'Guion', 'Montaje', 'DOP', 'Resumen'].

Hay que tener en cuenta que la búsqueda a la API de TMDB se realiza solo en función del título en inglés de la película y del año de realización. En caso de ambigüedad o de diferencias notables entre ambos atributos, es posible que haya algún error, por lo que se posibilita introducir manualmente el id de películas específicas. Esto se hace mediante el archivo de texto *filmid_whitelist*.

Cuando se realiza la búsqueda en TMDB, se puede realizar sobre el dataset de cine o el de TV, y el resultado puede ser un match perfecto, en el que coincidan literalmente título y año, o parcial, ya que TMDB devolverá los resultados más parecidos (aunque puede llegar a devolver un array vacío). Como en los datos originales no se discrimina entre cine y TV, la secuencia que prueba el script para determinar que se trata de la película buscada en el siguiente:
1. Se busca match exacto en cine.
2. Se busca match exacto en tv.
3. Se busca match parcial en cine.
4. Se busca match parcial en tv.

Mediante este proceso se determina el id de la película en TMDB, lo cual no se realiza si la película buscada está en la lista blanca. A partir de este id, se realiza la consulta completa de los atributos solicitados y se incorporan al dataset. Finalmente, este dataset se guarda en el archivo *dataset_topfilmtuiter.csv*. Durante el proceso, que puede tardar unos minutos, se indican por pantalla todos los casos en los que no se produzca un match exacto en cine, que es el caso mayoritario en este caso.

Este archivo, junto con el *Lista_votaciones.csv* generado en el paso 2.2, se utiliza como pase para el pbix que genera todas las estadísticas en Power BI.

Se incluyen también estos archivos, además el pbix, en la carpeta de Resultados.
