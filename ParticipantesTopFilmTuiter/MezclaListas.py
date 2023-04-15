import pandas as pd

lista_vieja=pd.read_csv('Ficheros_TFT1919/SeguidosTFT_08_04_2023.csv',sep=';')
lista_nueva=pd.read_csv('Ficheros_TFT1919/Seguidos10_08_04_2023.csv',sep=';')
print(lista_vieja)
#print(lista_nueva)

lista_vieja['nombre']=lista_vieja['0'].str.split(' - ', expand=True)[0]
lista_vieja['arroba']=lista_vieja['0'].str.split(' - ', expand=True)[1]

lista_nueva['nombre']=lista_nueva['0'].str.split(' - ', expand=True)[0]
lista_nueva['arroba']=lista_nueva['0'].str.split(' - ', expand=True)[1]


print(lista_nueva)
print(lista_vieja)


mezcla=pd.merge(lista_nueva,lista_vieja,on=['arroba','arroba'],how="outer",indicator=True)

print(mezcla)
mezcla.to_csv('Ficheros_TFT1919/Mezcla_08_04_2023.csv',sep=';')