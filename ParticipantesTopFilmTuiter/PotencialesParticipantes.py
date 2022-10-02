import tweepy
import pandas as pd

client = tweepy.Client(bearer_token='INTRODUCIR EL TOKEN', wait_on_rate_limit='True')

# Bucle que recupera todos los usuarios seguidos por los elegidos en el array y los guarda en lista


#user_ref=['paco_sanz','Danielquinn_', 'Aeneas_SVS', 'A_Karerina','Miguez_Diez','alicia_castilla']
user_ref=['topfilmtuiter']

##### Descomentar este bloque si se quiere utilizar como referencia los usuarios de un csv en lugar del array ########
# pd_user_ref=pd.read_csv('seguidos_TFT.csv',sep=';')
# usrs_truncados=pd_user_ref['0'].str.split(' - ', expand=True)[1]
# user_ref=usrs_truncados.tolist()
# print(user_ref)
#############################################################################

lista_amigos=[]

for usuarios in user_ref:
    print(usuarios)
    id_user = client.get_user(username=usuarios).data
    users = client.get_users_following(id=id_user.id,max_results=1000)
    if users.data is None:
        print('Cuenta candado')
    else:
        for user in users.data:
            # print(user.id)
            lista_amigos.append(user.name+' - '+user.username)
            # print(user.username)
df_participantes=pd.DataFrame(data=lista_amigos)
print(df_participantes)
participantes=df_participantes.value_counts()
participantes.to_csv('seguidos_seguidos_TFT.csv',sep=';')
