import tweepy
import pandas as pd
import time
import yaml
from yaml.loader import SafeLoader

"""
client = tweepy.Client(bearer_token='PONER AQUI EL BEARER TOKEN', wait_on_rate_limit='True')

"""

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

consumer_key = data['Twitter']['consumer_key']
consumer_secret = data['Twitter']['consumer_secret']
access_token = data['Twitter']['access_token']
access_token_secret = data['Twitter']['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

# Bucle que recupera todos los usuarios seguidos por los elegidos en el array y los guarda en lista


#user_ref=['paco_sanz','Danielquinn_', 'Aeneas_SVS', 'A_Karerina','Miguez_Diez','alicia_castilla']
user_ref=['marioquema','will_llermo','alicia_castilla','straubbhuillet','paco_sanz','Aeneas_SVS','braaisv','JuanJavato_24','Miguez_Diez','Danielquinn_']
#user_ref=['topfilmtuiter']
#user_ref=['marioquema']


##### Descomentar este bloque si se quiere utilizar como referencia los usuarios de un csv en lugar del array ########

#pd_user_ref=pd.read_csv('seguidos_tft2_20230219_min3.csv',sep=';')
#usrs_truncados=pd_user_ref['0'].str.rpartition(' - ')[2]
#user_ref=usrs_truncados.tolist()
#print(user_ref)


def lookup_user_list(followers_id, api):
    full_users = []
    users_count = len(followers_id)
    print(users_count)
    while True:
        try:
            for i in range(int(users_count / 100) + 1):
                user_ids = followers_id[i * 100:min((i + 1) * 100, users_count)]
                full_users.extend(api.lookup_users(user_id=user_ids))
        except tweepy.TweepyException as e:
            print('Error al obtener objetos de usuarios', e)
            time.sleep(15 * 60)
        return full_users

lista_amigos=[]

for usuarios in user_ref:
    print(usuarios)
    id_user = api.get_user(screen_name=usuarios)
    try:
        users_ids = api.get_friend_ids(user_id=id_user.id)
    except:
        print('Cuenta candado')
    contador = 0
    usuarios = lookup_user_list(users_ids, api)
    for bucle_usuarios in usuarios:
        #print(bucle_usuarios.name + ' - ' + bucle_usuarios.screen_name)
        lista_amigos.append(bucle_usuarios.name + ' - ' + bucle_usuarios.screen_name)

df_participantes=pd.DataFrame(data=lista_amigos)
print(df_participantes)
participantes=df_participantes.value_counts()
participantes.to_csv('Ficheros_TFT1919/Seguidos10_15_04_2023.csv',sep=';')

