import pandas as pd
import sys
from surprise import Dataset, Reader, SVD, SVDpp
from surprise import KNNBasic,  KNNWithMeans, KNNBaseline
from surprise.model_selection import cross_validate
import yaml
from yaml.loader import SafeLoader

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

# Cargo ese dataframe en el modelo de datos de dataset de Surprise y configuro escala de votacion en reader

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df_dataReco[['users', 'items', 'ratings']], reader)

# Pruebo un modelo SVD y lo evaluo con una cross validation

#svd = SVD(verbose=True, n_epochs=6)
#cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=3, verbose=False)

#knn = KNNBasic()
#cross_validate(knn, data, measures=['RMSE', 'MAE'], cv=3, verbose=False)


# prediccion = svd.predict(uid='Lobo_Lopez', iid='/film/the-deluge-1911/') # Ejemplo de prediccion individual

# Configuro la medida de similaridad (para el KNN)

sim_options = {
    "name": "pearson_baseline",
    "user_based": True,  # compute  similarities between items
    "min_support": 1,
    "shrinkage": 10
}


def genera_recos(data,reader):
    # Genera para todos los usuarios todas las predicciones de los items no consumidos/valorados
    print('Genera recos')
    trainset = data.build_full_trainset()
    svd = SVD(verbose=False, n_epochs=6)
    svd.fit(trainset)
    testset = trainset.build_anti_testset()
    predictions = svd.test(testset)
    lista_recos = []

    for uid, iid, true_r, est, _ in predictions:
        lista_recos.append([uid, iid, est])
        #print(lista_recos)

    df_lista_recos = pd.DataFrame(lista_recos, columns=['usuario','pelicula','rating_est'])
    return df_lista_recos


def genera_vecinos(data,reader):
    # Buscamos los vecinos mas proximos
    print('Genera vecinos')
    trainset = data.build_full_trainset()
    knn = KNNBasic(sim_options=sim_options)
    knn.fit(trainset)
    lista_vecinos = []
    matriz_similaridad = knn.compute_similarities()
    #print(matriz_similaridad)
    #df_matriz_sim = pd.DataFrame(matriz_similaridad)
    #df_matriz_sim.to_csv('matriz.csv', sep=';', index=False)

    for usuarios_inner in trainset.all_users():
        usuario_base = knn.trainset.to_raw_uid(usuarios_inner)
        vecinos = knn.get_neighbors(usuarios_inner, k=200)
        vecinos_nombre = (knn.trainset.to_raw_uid(inner_id) for inner_id in vecinos)
        contador=0
        for nombres_vecinos in vecinos_nombre:
            similaridad = matriz_similaridad[usuarios_inner][vecinos[contador]]

            elementos_usr1 = [i[0] for i in trainset.ur[usuarios_inner]]
            elementos_usr2 = [i[0] for i in trainset.ur[vecinos[contador]]]
            items_comunes = len(set(elementos_usr1).intersection(set(elementos_usr2)))
            lista_vecinos.append([usuario_base, nombres_vecinos, items_comunes+similaridad])
            contador += 1

    df_vecinos = pd.DataFrame(lista_vecinos, columns=['usuario_base', 'vecinos', 'similaridad'])

    return df_vecinos


df_vecinos = genera_vecinos(data, reader)
df_vecinos.to_csv(ruta_vecinos, sep=';',index=False)
df_vecinos.to_csv(ruta_vecinos_pbi, sep=';',index=False)
df_lista_recos = genera_recos(data,reader)
df_lista_recos.to_csv(ruta_recos, sep=';',index=False)
df_lista_recos.to_csv(ruta_recos_pbi, sep=';',index=False)
