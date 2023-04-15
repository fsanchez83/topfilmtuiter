import pandas as pd
import tweepy
import os
# import sys
import yaml
from yaml.loader import SafeLoader

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

with open('../config.cfg') as f:
    dataConfig = yaml.load(f, Loader=SafeLoader)

consumer_key = data['Twitter']['consumer_key']
consumer_secret = data['Twitter']['consumer_secret']
access_token = data['Twitter']['access_token']
access_token_secret = data['Twitter']['access_token_secret']

# Authentication with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

id_lista = dataConfig['General']['id_lista']

# update these for the tweet you want to process replies to 'name' = the account username and you can find the tweet id within the tweet URL
name = dataConfig['ParticipantesFinalesTFT']['name_cuenta']
tweet_id = dataConfig['ParticipantesFinalesTFT']['id_tuit']
lista_usrs = dataConfig['Resultados']['resultados_base']+id_lista+'/Procesamiento/usuarios'+id_lista+'.csv'

primera_carga = False

if os.stat(lista_usrs).st_size == 0:
    print('Primera carga de usuarios')
    primera_carga = True
else:
    df_usuarios = pd.read_csv(lista_usrs, sep=';')


replies = []
for tweet in tweepy.Cursor(api.search_tweets, q='to:'+name, result_type='recent').items(1000):
    if hasattr(tweet, 'in_reply_to_status_id_str'):
        if (tweet.in_reply_to_status_id_str==tweet_id):
            replies.append(tweet)

replies_limpios = []
for tweet in replies:
    if tweet.user.screen_name != dataConfig['ParticipantesFinalesTFT']['name_cuenta']:
        texto = tweet.text.split(" ")
        if len(texto) == 2:
            replies_limpios.append([tweet.text.split(" ")[1], ''])
        if len(texto) > 2:
            replies_limpios.append([tweet.text.split(" ")[1], tweet.text.split(" ")[2]])
        # print(tweet.text.split(" ")[2])

df_usuarios_nuevos = pd.DataFrame(data=replies_limpios, columns=['Usuarios', 'Lista'])

if primera_carga is False:
    usuarios_totales = pd.concat([df_usuarios, df_usuarios_nuevos])
    usuarios_totales = usuarios_totales.drop_duplicates(subset=['Usuarios'])
else:
    usuarios_totales = df_usuarios_nuevos

usuarios_totales.to_csv(lista_usrs, sep=';', index=False)
