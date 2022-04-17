# topfilmtuiter
Script para parsear listas de Letterboxd y generar resultados según los criterios de @topfilmtuiter.

Se recopilan en un dataframe, conservando su orden (ya sea o no una lista ordenada), todas las películas incluidas en las listas de Letterboxd de los usuarios de usuarios.txt con el nombre definido en nombre_lista.txt.
Según el orden de cada película en cada lista se le asigna una puntuación (definida en el propio main.py) y se recopila y suma en una lista final.

## Entradas
El programa no tiene parámetros de entrada. Es suficiente con ejecutar el main.py.

El programa utiliza como datos de entrada el contenido de dos archivos de texto:
- usuarios.txt. Listado de usuarios participantes en la encuesta
- nombre_lista.txt. Nombre de la lista de Letterboxd de la que se recopilarán los datos. Es decir, las listas de todos los usuarios deben tener el mismo nombre.

## Salidas
Se generan como salida dos archivos csv:
- Lista_votaciones.csv. Listado con todas las listas que se computan concatenadas, manteniendo la posición en cada lista individual y la puntuación correspondiente.
- Lista_votaciones_stats.csv. Lista agregada, sumando los puntos de todas las listas computadas y ordenada de mayor a menorn puntuación total
