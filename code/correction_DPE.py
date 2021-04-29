import pandas as pd
import requests
import json

fichier = 'data/DPE_CCPM.csv'

base = pd.read_csv(fichier, sep=';')
print(base.head())
result_attributs = {'latitude': ['geometry', 'coordinates', 1],
                    'longitude': ['geometry', 'coordinates', 0],
                    'result_label': ['properties', 'label'],
                    'result_score': ['properties', 'score'],
                    'result_type': ['properties', 'type'],
                    'result_id': ['properties', 'id'],
                    'result_housenumber': ['properties', 'housenumber'],
                    'result_name': ['properties', 'name'],
                    'result_street': ['properties', 'street'],
                    'result_postcode': ['properties', 'postcode'],
                    'result_city': ['properties', 'city'],
                    'result_context': ['properties', 'context'],
                    'result_citycode': ['properties', 'citycode'],
                    'result_oldcitycode': ['properties', 'citycode'],
                    'result_oldcity': ['properties', 'city'],
                    }

# for var in 
for i in base.index :
    print(i)
    if not str(base['code_insee_commune_actualise'][i])[:5] == str(base['result_citycode'][i])[:5]:
        adresse = base['nom_rue'][i]
        code_iris = base['code_insee_commune_actualise'][i]

        recherche = '+'.join(adresse.split())
        citycode = str(code_iris)[:5]
        url = f'https://api-adresse.data.gouv.fr/search/?q={recherche}&citycode={citycode}&limit=1'
        response = requests.get(url)
        r_json = response.json()
        # print(r_json)
        try:
            result = r_json['features'][0]
        except IndexError:
            result = {}
        for key in result_attributs:
            result_prov = result
            path = result_attributs[key]
            for step in path:
                print('step =',step)
                try : 
                    result_prov = result_prov[step]
                except KeyError:
                    result_prov = None
                    break
            # print('result =', result_prov)
            base.loc[i,(key,)] = result_prov
            # print(base.head())

base.to_csv(fichier, sep = ';')
