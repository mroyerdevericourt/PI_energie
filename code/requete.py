## ce fichier sert à coder l'interface code/data (étape 2)

import pandas as pd
import numpy as np
import requests
import json
import time

# try :
adresse = pd.read_csv('data/DLE-elec_adresse_2019.csv', ";")
#     print(adresse.head())
# except FileNotFoundError as e:
#     print (e)

villes = "Barbey. Blennes. Cannes Écluse. Chevry-en-Sereine. Courcelles-en-Bassée. Diant. Esmans. Forges. La Brosse-Montceaux. La Grande-Paroisse. Laval-en-Brie. Marolles-sur-Seine. Misy-sur-Yonne. Montereau-fault-Yonne. Montmachoux. Noisy-Rudignon. Saint-Germain-Laval. Salins. Thoury-Ferrottes. Varennes-sur-Seine. Voulx"
villes = villes.upper().split('. ')


base = adresse #[(adresse["NOM_COMMUNE"].isin(villes)) & pd.Series(map(lambda x : x[:2] == '77', adresse["CODE_IRIS"]))]
print (base.head())
longueur = base.shape[0]
# new_df["latitude"] = [None]*longueur
# new_df["longitude"] = [None]*longueur
# try: 
    # effacer la base de donnée créée

# base.to_csv('data/DLE-elec-2019-CCPM.csv',sep = ';')
i=0
def get_location(adresse, code_iris, ville=''):
    global i
    i += 1
    print(i)
    recherche = '+'.join((adresse + ville).split())
    citycode = str(code_iris)[:5]
    url = f'https://api-adresse.data.gouv.fr/search/?q={recherche}&citycode={citycode}&limit=1'
    status = 0
    while status != 200:
        reponse = requests.get(url)
        status = reponse.status_code
        datum = reponse.json()
        # if i > 320 :
        #     print(datum["features"])
        #     print(url)
        try : 
            lon, lat = datum["features"][0]["geometry"]["coordinates"]
        except IndexError:
            return None, None

        # properties = datum["features"][0]["properties"]
        return lat, lon


Res = list(map(get_location, base["ADRESSE"], base["CODE_IRIS"]))
Latit = [elem[0] for elem in Res]
Long = [elem[1] for elem in Res]
base = base.assign(latitude = Latit)
base = base.assign(longitude = Long)

print(base.head())
base.to_csv('data/DLE-elec-2019-geocoded.csv',sep = ';')