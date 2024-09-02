import pandas as pd
import yaml
from yaml.loader import SafeLoader

## Script para cargar los csv de follows y filtrarlos dejando solo los usuarios que han
# participado en la edicion en cuestion de TFT. Y lo deja en las carpetas de resultados
# y de PBI

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

id_lista = dataConfig['General']['id_lista']

csv_followers_path = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followers.csv'

csv_followings_path = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followings.csv'

followers_TFT = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followers_'+id_lista+'.csv'

followings_TFT = dataConfig['Resultados']['resultados_base'] + id_lista + \
                '/Procesamiento/followings_'+id_lista+'.csv'

followers_TFT_pbi = dataConfig['Resultados'][
                        'base_pbi']+'follows/followers_'+id_lista+'.csv'
followings_TFT_pbi = dataConfig['Resultados'][
                        'base_pbi']+'follows/followings_'+id_lista+'.csv'

df_followers = pd.read_csv(csv_followers_path)
df_followings = pd.read_csv(csv_followings_path)

print(df_followings)

df_followers_filtrado = df_followers[df_followers['Follower'].isin(df_followers['Usuario'])]
df_followings_filtrado = df_followings[df_followings['Following'].isin(df_followings[
                                                                         'Usuario'])]

print(df_followings_filtrado)

df_followers_filtrado.to_csv(followers_TFT, index=False)
df_followings_filtrado.to_csv(followings_TFT, index=False)

df_followers_filtrado.to_csv(followers_TFT_pbi, index=False)
df_followings_filtrado.to_csv(followings_TFT_pbi, index=False)
