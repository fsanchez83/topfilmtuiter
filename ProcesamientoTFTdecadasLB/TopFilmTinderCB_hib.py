import pandas as pd
import sys
import ast
import yaml
import numpy as np
from yaml.loader import SafeLoader

def parte_matriz(df):
    # Obtiene la lista de todas las columnas del dataframe
    columnas = M_carac_filtrada.columns

    # Define los nombres de los prefijos
    prefijos = ["Pelis_", "Director_", "Genero_", "Fecha_", "Pais_"]

    # Crea un diccionario para almacenar los dataframes separados por prefijo
    dataframes_por_prefijo = {}

    # Itera sobre cada prefijo y filtra las columnas correspondientes
    for prefijo in prefijos:
        columnas_prefijo = [col for col in columnas if col.startswith(prefijo)]
        df_prefijo = M_carac_filtrada[columnas_prefijo]
        dataframes_por_prefijo[prefijo] = df_prefijo

    # Acceso a dataframes independientes por su prefijo
    df_pelis = dataframes_por_prefijo["Pelis_"]
    df_director = dataframes_por_prefijo["Director_"]
    df_genero = dataframes_por_prefijo["Genero_"]
    df_fecha = dataframes_por_prefijo["Fecha_"]
    df_pais = dataframes_por_prefijo["Pais_"]

    return df_pelis, df_director, df_genero, df_fecha, df_pais

def similitud_M_simple(matriz_pelis):
    matriz_similitud = np.dot(matriz_pelis, matriz_pelis.T)
    # Normalizar dividiendo por las varianzas (diagonal) y quitar diagonal
    variances = np.diag(matriz_similitud)
    normalized_matrix = matriz_similitud / np.sqrt(np.outer(variances, variances))
    numero_peliculas_comunes_entre_usuarios = normalized_matrix - np.diag(np.diag(normalized_matrix))
    # Normalizar dividiendo por el valor de los usuarios mas similares
    max_element = np.max(numero_peliculas_comunes_entre_usuarios)
    numero_peliculas_comunes_entre_usuarios = numero_peliculas_comunes_entre_usuarios / max_element
    return numero_peliculas_comunes_entre_usuarios

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)

id_lista = dataConfig['General']['id_lista']

ruta_vecinos = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/lista_vecinos_'+id_lista+'.csv'
ruta_vecinos_pbi = dataConfig['Resultados']['base_pbi']+'topfilmtinder/vecinos/lista_vecinos_'+id_lista+'.csv'
ruta_recos = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/lista_recos_'+id_lista+'.csv'
ruta_recos_pbi = dataConfig['Resultados']['base_pbi']+'topfilmtinder/recos/lista_recos_'+id_lista+'.csv'

# Recupero el fichero de votaciones individuales y preparo dataset con las 3 columnas necesarias: users, items, ratings
votaciones = pd.read_csv(dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/Lista_votaciones_'+id_lista+'.csv')

usuarios_bruto = (votaciones['url'].str.replace('https://letterboxd.com/', "")).str.split('/').to_list()
usuarios = pd.DataFrame(data=usuarios_bruto)[0]

df_dataReco = pd.DataFrame(data=usuarios)
df_dataReco['items'] = votaciones['url_peli']
df_dataReco['ratings'] = votaciones['Puntos']
df_dataReco = df_dataReco.rename(columns={0: 'users'})

# Creo las matrices usuarios-peliculas y peliculas-caracteristicas
matriz_usr_peli = df_dataReco.pivot(index='users', columns='items', values='ratings').fillna(0)

# Convierto los literales en listas y aislo cada posible valor, creando categorias unicas con OHE
df_caracteristicas = pd.read_csv(dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/dataset_'+id_lista+'.csv', sep=';')
df_caracteristicas = df_caracteristicas[['url_peli','Fecha', 'Pais', 'Director', 'Generos']]
df_caracteristicas['Fecha'] = df_caracteristicas['Fecha'].str[:4].astype(int)//10*10
df_caracteristicas['Generos'] = df_caracteristicas['Generos'].apply(ast.literal_eval)
df_caracteristicas['Director'] = df_caracteristicas['Director'].apply(ast.literal_eval)

directores_unicos = df_caracteristicas['Director'].explode().unique()
generos_unicos = df_caracteristicas['Generos'].explode().unique()
pelis_unicas = df_caracteristicas['url_peli'].explode().unique()

for pelis in pelis_unicas:
    df_caracteristicas['Pelis_'+pelis] = df_caracteristicas['url_peli'].apply(lambda x: pelis in x).astype(int)

for genero in generos_unicos:
    df_caracteristicas['Genero_'+str(genero)] = df_caracteristicas['Generos'].apply(lambda x: genero in x).astype(int)

for director in directores_unicos:
    df_caracteristicas['Director_'+str(director)] = df_caracteristicas['Director'].apply(lambda x: director in x).astype(int)

# Borro las columnas con los literales una vez hecho el OHE
df_carac_generos = df_caracteristicas.drop(columns=['Generos','Director'])
df_encoded = pd.get_dummies(df_carac_generos, columns=['Fecha', 'Pais'],dummy_na=False, dtype=int)
df_encoded = df_encoded.set_index('url_peli')

# df_encoded es la matriz de peliculas x caracteristicas
# matriz_usr_peli es la matriz de usuarios x peliculas
# Busco las peliculas comunes de ambas matrices para evitar si errores si hbieran algun desajuste

peliculas_comunes = matriz_usr_peli.columns.intersection(df_encoded.index)

# Filtro y reordeno ambas matrices para que sigan el mismo orden de peliculas
M_usr_filtrada = matriz_usr_peli[peliculas_comunes]
M_carac_filtrada = df_encoded.loc[peliculas_comunes]

# Parto la matriz general de caracteristicas en matrices por cada grupo de caracteristicas
df_pelis, df_director, df_genero, df_fecha, df_pais = parte_matriz(M_carac_filtrada)

# Calculo las similitudes entre usuarios para cada bloque de caracteristicas
Mat_sim_peli = similitud_M_simple(np.dot(M_usr_filtrada.values, df_pelis.values))
Mat_sim_dir = similitud_M_simple(np.dot(M_usr_filtrada.values, df_director.values))
Mat_sim_gen = similitud_M_simple(np.dot(M_usr_filtrada.values, df_genero.values))
Mat_sim_fecha = similitud_M_simple(np.dot(M_usr_filtrada.values, df_fecha.values))
Mat_sim_pais = similitud_M_simple(np.dot(M_usr_filtrada.values, df_pais.values))

# Obtengo el peso de cada bloque de caracteristicas (inversa del valor medio de similitudes)
w_peli = 1/np.mean(Mat_sim_peli)
w_dir = 1/np.mean(Mat_sim_dir)
w_gen = 1/np.mean(Mat_sim_gen)
w_fecha = 1/np.mean(Mat_sim_fecha)
w_pais = 1/np.mean(Mat_sim_pais)

peso_total = w_peli + w_dir + w_gen + w_fecha + w_pais

# Calculo la matriz total de similitudes ponderando las similitudes parciales por bloque
matriz_total = (w_peli*Mat_sim_peli + w_dir*Mat_sim_dir + w_gen*Mat_sim_gen + w_fecha*Mat_sim_fecha + w_pais*Mat_sim_pais)/peso_total
maximo_matriz_total = np.max(matriz_total)
matriz_total = (100*matriz_total)/maximo_matriz_total

# Convierto la matriz total en el listado de similitudes en formato exportable a csv

i = 0
j = 0
lista_vecinos = []
for usuarios_base in M_usr_filtrada.index:
    for usuarios_vecinos in M_usr_filtrada.index:
        if i!= j:
            peso_abs = w_peli * Mat_sim_peli[i, j]+w_dir * Mat_sim_dir[i, j]+w_gen * Mat_sim_gen[i, j]+w_fecha * Mat_sim_fecha[i, j]+w_pais * Mat_sim_pais[i, j]
            lista_vecinos.append([usuarios_base, usuarios_vecinos, matriz_total[i,j], 100*w_peli*Mat_sim_peli[i,j]/peso_abs, 100*w_dir*Mat_sim_dir[i,j]/peso_abs, 100*w_gen*Mat_sim_gen[i,j]/peso_abs, 100*w_fecha*Mat_sim_fecha[i,j]/peso_abs, 100*w_pais*Mat_sim_pais[i,j]/peso_abs])
        j += 1
    i += 1
    j = 0

df_vecinos = pd.DataFrame(lista_vecinos, columns=['usuario_base', 'vecinos', 'similaridad','imp_pelis','imp_dir','imp_gen','imp_fecha','imp_pais'])
df_vecinos.to_csv(ruta_vecinos, sep=';',index=False)
df_vecinos.to_csv(ruta_vecinos_pbi, sep=';',index=False)


########  RECOMENDACION PELICULAS HIBRIDA #############
### CB - Multiplicar la matriz usuarios-caracteristicas por la matriz caract-peliculas

Matriz_usr_carac = np.dot(M_usr_filtrada.values, M_carac_filtrada.values)
Matriz_reco = np.dot(Matriz_usr_carac, M_carac_filtrada.T)

# Recupero matriz similitudes vecinos y normalizo el peso de los vecinos para que la suma de sus pesos sea 1
matriz_np = np.array(matriz_total)
sumas_filas = matriz_np.sum(axis=1)
matriz_total = matriz_np / sumas_filas[:, np.newaxis]

# Matriz_reco_vecinos es la estimacion de puntuacion que tiene una peli para un usuario a partir de la afinidad con el resto de usuarios
# Se normalizan los valores por maximo
Matriz_reco_vecinos = np.dot(matriz_total, Matriz_reco)
matriz_np = np.array(Matriz_reco_vecinos)
sumas_filas = matriz_np.max(axis=1)
Matriz_reco_vecinos = matriz_np / sumas_filas[:, np.newaxis]

# Matriz_reco en la estimacion CB para cada usuario. Se normalizan los valores por maximo
matriz_np = np.array(Matriz_reco)
sumas_filas = matriz_np.max(axis=1)
Matriz_reco = matriz_np / sumas_filas[:, np.newaxis]

# Con los valores de ambas matrices se calcula la estimacion final del reco hibrido.
# 50% de peso del CB (caracteristicas preferidas por el usuario) y 50% colaborativo (peliculas preferidas para otros usuarios)
# El resultado se almacena en una lista para exportar a csv
lista_recos_hib = []
i_usr = 0
i_pel = 0
for usuarios_base in M_usr_filtrada.index:
    pelis_usuario = df_dataReco[df_dataReco['users']==usuarios_base]['items'].to_list()
    for peliculas in M_usr_filtrada.columns:
        if peliculas not in pelis_usuario:
            #estimacion = 50*(Matriz_reco[i_usr,i_pel] + Matriz_reco_vecinos[i_usr,i_pel])
            estimacion = 100*(Matriz_reco[i_usr,i_pel])
            lista_recos_hib.append([usuarios_base, peliculas, estimacion])

        i_pel += 1
    i_usr += 1
    i_pel = 0
df_lista_recos = pd.DataFrame(lista_recos_hib, columns=['usuario','pelicula','rating_est'])
df_lista_recos.to_csv(ruta_recos, sep=';',index=False)
df_lista_recos.to_csv(ruta_recos_pbi, sep=';',index=False)
