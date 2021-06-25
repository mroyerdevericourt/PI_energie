### Ce programme va associer chaque adresse des bases DLE (electricité et gaz) à des coordonnées GPS 
### à l'aide de l'API d'Etalab 
### Il utilise le multiprocessing pour pallier au délai aller/retour de l'API (env. 0,2s).

import multiprocessing as mp
import pandas as pd
import numpy as np
import requests
import json
import time

### Pour chaque ligne de la base DLE, la fonction 'send' crée l'url de requête et l'insère dans une queue
def send(queue, base):
    for i in base.index:
        adresse = base['ADRESSE'][i]
        code_iris = base['CODE_IRIS'][i]
        citycode = str(code_iris)[:5]
        if type(adresse) != str:
            url = f'https://api-adresse.data.gouv.fr/search/?q=citycode={citycode}&limit=1'
        else :
            recherche = '+'.join(adresse.split())
            url = f'https://api-adresse.data.gouv.fr/search/?q={recherche}&citycode={citycode}&limit=1'
        queue.put((i, url))
    for _ in range(nb_proc):
        queue.put((-1, None))

### La fonction 'make_requests' récupère chaque URL de la queue, exécute la requete, insère le résultat dans une autre queue.
### Plusieurs process vont excécuter cett fonction. 
def make_requests(queue_url, queue_json):
    running = True
    while running:
        url_id, url = queue_url.get()
        if url_id == -1 :
            # print(f'ca va se finir pour {pid}')
            running = False
            break
        status = 0
        while status != 200:
            reponse = requests.get(url)
            status = reponse.status_code
        datum = reponse.json()
        queue_json.put((url_id, datum))

### 'class_requests' remet les résultats de la queue dans le bon ordre.
### Elle en profite aussi pour introduire un pourcentage d'avancée du programme.
def class_requests(base, queue_json, classed_json, long, sortie):
    print("Requêtes à l'API Etalab en cours")
    tampon = {}      # Le tampon est un dictionnaire qui associe à un identifiant ses données. 
                     # Il est rempli lorsque la première donnée de la queue n'est pas l'identifiant recherché.
    cpt = 0
    for i in base.index:
        cpt += 1
        print(f'{cpt*100/long: .3f} %')
        try :
            right_json = tampon[i]
            del tampon[i]
        except KeyError:
            j, datum = queue_json.get()
            while j != i:
                tampon[j] = datum
                j, datum = queue_json.get()
            right_json = datum
        classed_json.append(right_json)
    print('Classement des requêtes terminé.')
    treat_json(base, classed_json, sortie)

### Cette fonction extrait du json les données qui nous intéressent et les enregistre dans le csv.
def treat_json(base, L, sortie):
    erreur = 0
    Lon = []
    Lat = []
    Score = []
    for elem in L:
        try : 
            lon, lat = elem["features"][0]["geometry"]["coordinates"]
            score = elem["features"][0]["properties"]["score"]
        except IndexError:
            erreur += 1
        Lon.append(lon)
        Lat.append(lat)
        Score.append(score)
    print(f'Traitement terminé, il y a eu {erreur} erreur(s)')
    print('Encryptage dans', sortie)
    base = base.assign(latitude = Lat, longitude = Lon, score = Score)
    print(base.head())
    base.to_csv(sortie, sep = ';')
    print('\n Encryptage terminé')
    



nb_proc = 10

if __name__ == '__main__':
    
    for data_type in {'elec', 'gaz'}:
        fichier = f'data/DLE-{data_type}_adresse_2019.csv'
        fichier_sortie_geocoded = fichier[:-4] + '-geocoded.csv'
        base = pd.read_csv(fichier, ";")

        long_base = base.shape[0]
        print('Geocodage de', fichier)
        
        url_queue = mp.Queue()
        json_queue = mp.Queue()
        classed_json = []
        url_process = mp.Process(target = send, args = (url_queue, base,))
        url_process.start()
        requests_processes = [mp.Process(target = make_requests, args = (url_queue, json_queue)) for pid in range(nb_proc)]
        for proc in requests_processes:
            proc.start()
        classing_proc = mp.Process(target = class_requests, args = (base, json_queue, classed_json, long_base, fichier_sortie_geocoded))
        classing_proc.start()
        
        classing_proc.join()
        url_process.join()
        for proc in requests_processes:
            proc.join()