import multiprocessing as mp
import pandas as pd
import numpy as np
import requests
import json
import time

def send(queue, base):
    for i in base.index:
        adresse = base['ADRESSE'][i]
        code_iris = base['CODE_IRIS'][i]

        recherche = '+'.join(adresse.split())
        citycode = str(code_iris)[:5]
        url = f'https://api-adresse.data.gouv.fr/search/?q={recherche}&citycode={citycode}&limit=1'
        queue.put((i, url))
    for _ in range(nb_proc):
        queue.put((-1, None))

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

def class_requests(base, queue_json, classed_json, long, sortie):
    print("Requêtes à l'API Etalab en cours")
    tampon = {}
    cpt = 0
    for i in base.index:
        cpt += 1
        print(f'{cpt*100/long: .2f} %')
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

def treat_json(base, L, sortie):
    erreur = 0
    Lon = []
    Lat = []
    Geo_id = []
    Score = []
    for elem in L:
        try : 
            lon, lat = elem["features"][0]["geometry"]["coordinates"]
            geo_id = elem["features"][0]["properties"]['id']
            score = elem["features"][0]["properties"]["score"]
        except IndexError:
            erreur += 1
        Lon.append(lon)
        Lat.append(lat)
        Geo_id.append(geo_id)
        Score.append(score)
    print(f'Traitement terminé, il y a eu {erreur} erreur(s)')
    print('Encryptage dans', sortie)
    base = base.assign(latitude = Lat, longitude = Lon, id = geo_id, score = Score)
    print(base.head())
    base.to_csv(sortie, sep = ';')
    print('\n Encryptage terminé')
    



nb_proc = 10

if __name__ == '__main__':
    
    for data_type in {'elec', 'gaz'}:
        fichier = f'data/DLE-{data_type}_adresse_2019.csv'
        fichier_sortie = f'data/DLE-{data_type}-2019-CCPM.csv'
        fichier_sortie_geocoded = fichier_sortie[:-4] + '-geocoded.csv'
        adresse = pd.read_csv(fichier, ";")

        villes = "Barbey. Blennes. Cannes Écluse. Chevry-en-Sereine. Courcelles-en-Bassée. Diant. Esmans. Forges. La Brosse-Montceaux. La Grande-Paroisse. Laval-en-Brie. Marolles-sur-Seine. Misy-sur-Yonne. Montereau-fault-Yonne. Montmachoux. Noisy-Rudignon. Saint-Germain-Laval. Salins. Thoury-Ferrottes. Varennes-sur-Seine. Voulx"
        villes = villes.upper().split('. ')

        base = adresse[(adresse["NOM_COMMUNE"].isin(villes)) & pd.Series(map(lambda x : x[:2] == '77', adresse["CODE_IRIS"]))]

        base.to_csv(fichier_sortie, sep = ';')

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