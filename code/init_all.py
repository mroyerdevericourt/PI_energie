## ce fichier sert à géocoder la table entière de données.

import pandas as pd
import numpy as np
import requests
import json
import time


try : 
    adresse = pd.read_csv('data/DLE-elec-2019-geocoded.csv', ";")
except FileNotFoundError :
    adresse = pd.read_csv('data/DLE-elec_adresse_2019.csv', ";")
base = adresse
print(base.head())
longueur = base.shape[0]
N = 1000
i = begin(base)

while i < longueur :
    j = 0
    Res = [None]*longueur
    while j < N and i < longueur:
        j += 1
        i += 1
        print(f'Global = {i*100/longueur:.4f} %, Cycle = {j*100/N:.2f} %')
    
    Latit = [elem[0] for elem in Res]
    Long = [elem[1] for elem in Res]
    base = base.assign(latitude = Latit)
    base = base.assign(longitude = Long)
    
    base.to_csv('data/DLE-elec-2019-geocoded.csv',sep = ';')



def get_location(adresse, code_iris, ville=''):
    recherche = '+'.join((adresse + ville).split())
    citycode = str(code_iris)[:5]
    url = f'https://api-adresse.data.gouv.fr/search/?q={recherche}&citycode={citycode}&limit=1'
    status = 0
    while status != 200:
        reponse = requests.get(url)
        status = reponse.status_code
    datum = reponse.json()
    try : 
        lon, lat = datum["features"][0]["geometry"]["coordinates"]
    except IndexError:
        return None, None
    properties = datum["features"][0]["properties"]
    return lat, lon, properties


# Res = list(map(get_location, base["ADRESSE"], base["CODE_IRIS"]))
# Latit = [elem[0] for elem in Res]
# Long = [elem[1] for elem in Res]
# base = base.assign(latitude = Latit)
# base = base.assign(longitude = Long)

# print(base.head())
# base.to_csv('data/DLE-elec-2019-geocoded.csv',sep = ';')