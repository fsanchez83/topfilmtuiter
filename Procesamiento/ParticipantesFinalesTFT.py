import pandas as pd
import tweepy

# Oauth keys
consumer_key = "COMPLETAR"
consumer_secret = "COMPLETAR"
access_token = "COMPLETAR"
access_token_secret = "COMPLETAR"

# Authentication with Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Actualiza esto segun el tweet del que quieras recoger las respuestas fijando en 'name' el nombre de usuario
# de la cuenta del tweet y en tweet_id el id de ese tweet.
name = 'topfilmtuiter'
tweet_id = '1553890672201056257'

df_usuarios=pd.read_csv('usuarios.txt')

replies = []
for tweet in tweepy.Cursor(api.search_tweets,q='to:'+name, result_type='recent').items(1000):
    if hasattr(tweet, 'in_reply_to_status_id_str'):
        if (tweet.in_reply_to_status_id_str==tweet_id):
            replies.append(tweet)

replies_limpios = []
for tweet in replies:
    replies_limpios.append(tweet.text.split(" ")[1])

df_usuarios_nuevos = pd.DataFrame(data=replies_limpios,columns=['Usuarios'])

usuarios_totales = pd.concat([df_usuarios, df_usuarios_nuevos])
usuarios_totales = usuarios_totales.drop_duplicates()

usuarios_totales.to_csv('usuarios.txt',index=False)

