import tweepy
import pandas as pd
import yaml
from yaml.loader import SafeLoader

#client = tweepy.Client(bearer_token='AAAAAAAAAAAAAAAAAAAAAHj9WAEAAAAAiL3Nomevd1AUVigS4JNZ3EO%2F5Dg%3D1wY54oSeYfTbI1iYCWV5LHZ2udb0ta6SoukomCAt6yiF9n5Rnj', wait_on_rate_limit='True')
# Las claves de la cuenta desde la que se quiera seguir a los usuarios de la lista 'lista_follow.csv'

with open('../secrets.cfg') as f:
    data = yaml.load(f, Loader=SafeLoader)

consumer_key = data['Twitter']['consumer_key']
consumer_secret = data['Twitter']['consumer_secret']
access_token = data['Twitter']['access_token']
access_token_secret = data['Twitter']['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

# Usuarios que se quiere seguir

pd_user_ref = pd.read_csv('lista_follow.csv',sep=';')
user_ref = pd_user_ref['usr'].tolist()
print(user_ref)

for usuario in user_ref:
    user = api.get_user(screen_name=usuario)
    print(user.name)
    user.follow()
