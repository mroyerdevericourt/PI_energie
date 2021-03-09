## ce fichier sert à coder l'interface code/data (étape 2)

import pandas as pd
import numpy as np

try :
    fichier = pd.read_csv('data/DLE-elec_adresse_2018.csv', ";")
    print(fichier.head())
except FileNotFoundError as e:
    print (e)