import pandas as pd
import math

elec = pd.read_csv('data/DLE-elec-2019-CCPM-geocoded.csv', sep = ';')
gaz = pd.read_csv('data/DLE-gaz-2019-CCPM-geocoded.csv', sep = ';')
dpe = pd.read_csv('data/DPE_CCPM.csv', sep = ';')

def convert_e2f(string):
    return float(string[0]+string[2:8]) * 10**(int(string[9:]) - 6)

limite_classe_energie = {50 : 'A', 90 : 'B', 150 : 'C', 230 : 'D', 330 : 'E', 450 : 'F', math.inf : 'G'}
limite_classe_ges = {5 : 'A', 10 : 'B', 20 : 'C', 35 : 'D', 55 : 'E', 80 : 'F', math.inf : 'G'}
type_encadrement = {'consommation_energie' : limite_classe_energie, 'estimation_ges' : limite_classe_ges}
def encadrement(val, inter):
    for key in inter:
        classe = inter[key]
        if key > val:
            break
    return classe


elec['CONSO'] = elec['CONSO'].apply(convert_e2f)
gaz['CONSO'] = gaz['CONSO'].apply(convert_e2f)
# Aggregation sur l'id d'etalab

# toBfirsted = {elec : ['FILIERE', 'CODE_GRAND_SECTEUR']}
# toBmeaned = {elec : }
# toBsumed

# bases_useful = []
# for base in [elec, gaz]:
#     groupe = base.groupby('id')
#     firsted = groupe[['FILIERE', 'CODE_GRAND_SECTEUR', 'ADRESSE', 'NOM_COMMUNE']].nth(0)
#     meaned = groupe[['latitude', 'longitude']].mean()
#     sumed = groupe[['PDL', 'CONSO']].sum()
#     grouped = firsted.merge(meaned, on = 'id')
#     base_useful = grouped.merge(sumed, on = 'id')
#     bases_useful.append(base_useful)
#     print(base_useful)

# elec, gaz = bases_useful

### On met en forme gaz et elec, et on les fusionne sur leurs adresses
elec.rename(columns = {'CONSO': 'CONSO_elec', 'PDL' : 'PDL_elec', 'id': 'id_geo'}, inplace = True)
gaz.rename(columns = {'CONSO': 'CONSO_gaz', 'PDL' : 'PDL_gaz', 'id': 'id_geo'}, inplace = True)
keys = ('FILIERE', 'CODE_GRAND_SECTEUR', 'ADRESSE', 'NOM_COMMUNE', 'latitude', 'longitude', 'id_geo', 'score')
joined = elec.merge(gaz, on = keys, how = 'outer')

### On introduit la consommation brute du logement, qui nous servira par la suite pour faire des groupements
for elem in {'consommation_energie', 'estimation_ges'}:
    dpe[elem + '_brut'] = (dpe[elem] * dpe['surface_habitable'])


### On traite les DPE
# print(dpe[['consommation_energie', 'consommation_energie_brut', 'surface_habitable', 'estimation_ges', 'estimation_ges_brut']])
dpe.rename(columns = {elem : elem + '_dpe' for elem in ['commune', 'type_voie', 'numero_rue', 'nom_rue', 'id']} , inplace = True)
dpe.rename(columns = {'result_id': 'id_geo', 'result_score' : 'score'} , inplace = True)

### On joint tout
all_join = dpe.merge(joined, on = ('latitude', 'longitude', 'score', 'id_geo'), how = 'outer')
all_join.to_csv('data/test.csv', ';')


### On va distinguer les colonnes intéressantes en fonction de l'opération d'agrégation, et on les joint de nouveau
grouped = all_join.groupby('id_geo')
sumed = grouped[['consommation_energie_brut', 'estimation_ges_brut', 'surface_habitable', 'PDL_elec', 'CONSO_elec', 'PDL_gaz', 'CONSO_gaz']].sum()
meaned = grouped[['latitude', 'longitude', 'score']].mean()
firsted = grouped[['classe_consommation_energie', 'classe_estimation_ges', 'secteur_activite', 'commune_dpe', 'type_voie_dpe', 
                   'numero_rue_dpe', 'nom_rue_dpe', 'result_label', 'result_type', 'result_housenumber', 'result_name', 'NOM_COMMUNE', 'ADRESSE', 'FILIERE', 'CODE_GRAND_SECTEUR']].first()


merge1 = firsted.merge(meaned, on = 'id_geo')
dpe_dle = merge1.merge(sumed, on = 'id_geo')


### On rajoute les classes de consommation et d'émission
for elem in {'consommation_energie', 'estimation_ges'}:
    dens = (dpe_dle[elem + '_brut'] / dpe_dle['surface_habitable'])
    classes = dens.apply(encadrement, args = (type_encadrement[elem],))
    dpe_dle['classe_' + elem] = classes

dpe_dle.to_csv('data/dpe_dle-pertinent.csv', ';')





# def convert_e2f(string):
#     return float(string[0] + string[2:8]) * 10**int(string[9:])
# print(gaz.dtypes)
# for base in [elec, gaz]:
#     for key in ["CONSO", "PDL", "latitude", "longitude", "score"]:
#         print(base[key])
#         # base[key].transform(convert_e2f)

# for key in ["consommation_energie", "estimation_ges", "surface_habitable", "latitude", "longitude", "result_score"]:
#     # dpe[key].transform(convert_e2f)
#     pass


# joined = gaz.merge(elec, 'outer', "id")
# print(joined)
# dpe_grouped = dpe.groupby("result_id")
# print(dpe_grouped)

# joined = joined.merge(dpe, 'outer', left_on = "id", right_on = "result_id")
# print(joined)