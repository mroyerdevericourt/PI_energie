# Ce code correspond à la version python du code de la carte disponible sur le notebook 


import folium as fm
import csv
import pandas as pd
from folium.plugins import MarkerCluster
from folium.plugins import Search

cs = 3

#création du fond de carte (on prend un point arbitraitre dans la communauté de communes de Montereau)
m = fm.Map(location=[48.39406536332271, 2.9518367606924776], zoom_start=12)

#création du groupe DLE (à afficher ou cacher sur la carte finale 'm') 
DLE_group = fm.FeatureGroup(name="DLE").add_to(m)

base_elec = pd.read_csv("../data/DLE-elec-2019-CCPM-geocoded.csv", ";")
base_gaz = pd.read_csv("../data/DLE-gaz-2019-CCPM-geocoded.csv", ";")

#documentation
dico_secteur = {'A': 'Agriculture', 'I' : 'Industriel', 'X' : 'Professionnel non affecté', 'R' : 'Résidentiel', 'T' : 'Tertiaire'}
dico_filiere = {'E' : 'Electricité' , 'G' : 'Gaz'}
dico_couleur_filiere = {'E' : 'blue', 'G' : 'green' }

def significatifs(data,c):
    """
    convertit la chaine de caractère data
    qui est forcément de la forme X,XXXXe+XX
    en une chaine en écriture scientifique 
    avec c chiffres significatifs
    """
    new = data[:2]
    i = 0
    
    while 1+i <= c :
        new += data[2+i]
        i += 1
        
    end = 'e'+ data[-3] + data[-2] + data[-1]
    return new + end        
    
def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-bottom leaflet-left').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(fm.Element(script + css))

    return folium_map

#code couleur pour distinguer Gaz et Elec dans les DLE
m = add_categorical_legend(m, 'Filiere (DLE)',
                             colors = ['#64cd1e','#03cafc'],
                           labels = ['Gaz', 'Electricité'])

def non_breaking_spaces(data):
    """
    remplace les espaces dans un str par des &nbsp
    &nbsp = non breaking space en HTML
    évite des retours à la ligne excessifs
    """
    new = ''
    for i in range(len(data)):
        if data[i] != ' ':
            new += data[i]
        else:
            new += '&nbsp'
    return new

def pourcentage(score):
    """
    écrit le score en pourcentage
    """
    fl = float(score)
    fl = 100*fl
    return str(int(fl))

#regroupement des points (clusters) pour éviter les amas de markers
cluster_DLE_all = MarkerCluster().add_to(DLE_group)

##pour l'électricité

for i in range(len(base_elec)):

    data = base_elec.loc[i]

    geocode = [data['latitude'],data['longitude']]

    name_tip = non_breaking_spaces(data['ADRESSE'])
    filiere = data['FILIERE']
    code_grand_secteur = data['CODE_GRAND_SECTEUR']
    name_grand_secteur = dico_secteur[code_grand_secteur]
    color_filiere = dico_couleur_filiere[filiere]

    score = pourcentage(data['score'])
    
    fm.Marker(geocode,
    popup=f"<p><strong>{name_tip}</strong></p><p><strong>Secteur&nbsp:&nbsp</strong>{name_grand_secteur}<p>{str(data['PDL'])}&nbsppoint(s)&nbspde&nbsplivraison</p><p><strong>Consommation</strong>: {significatifs(data['CONSO'],cs)}&nbspMWh</p><p><em>Fiable&nbspà&nbsp{score}&nbsp%</em></p>",tooltip=name_tip,icon = fm.Icon(color=color_filiere,  icon_color = '#ffffff')).add_to(cluster_DLE_all)



##pour le gaz

for i in range(len(base_gaz)):

  data = base_gaz.loc[i]

  geocode = [data['latitude'],data['longitude']]

  name_tip = non_breaking_spaces(data['ADRESSE'])
  filiere = data['FILIERE']
  code_grand_secteur = data['CODE_GRAND_SECTEUR']
  name_grand_secteur = dico_secteur[code_grand_secteur]
  color_filiere = dico_couleur_filiere[filiere]

  score = pourcentage(data['score'])
    
  fm.Marker(geocode, name = name_tip,
  popup=f"<p><strong>{name_tip}</strong></p><p><strong>Secteur&nbsp:&nbsp</strong>{name_grand_secteur}<p>{str(data['PDL'])}&nbsppoint(s)&nbspde&nbsplivraison</p><p><strong>Consommation</strong>:&nbsp{significatifs(data['CONSO'],cs)}&nbspMWh</p><p><em>Fiable&nbspà&nbsp{score}&nbsp%</em></p>",tooltip=name_tip,icon = fm.Icon(color=color_filiere,  icon_color = '#ffffff')).add_to(cluster_DLE_all)


# POUR LES DPE
base_DPE = pd.read_csv('../data/dpe_dle-pertinent.csv', ';')

#groupe pour le menu d'affichage
DPE_conso_group = fm.FeatureGroup(name="DPE").add_to(m)

#cluster
cluster_DPE_conso = MarkerCluster().add_to(DPE_conso_group)

#légende (couleurs de la classe)
colors_conso = ['#039033', '#51b016', '#c8d200', '#fcea26', '#f8bb01', '#eb690b', '#e30c1c']
labels_conso = ["A  (moins de 50)", 'B  (entre 50 et 90)', 'C  (entre 90 et 150)','D  (entre 150 et 230)','E  (entre 230 et 330)','F  (entre 331 et 450)', 'G  (plus de 450)']

m = add_categorical_legend(m," DPE - Classes de consommation énergétique <br>(en kWh d'énergie primaire par m^2 par an)", colors = colors_conso, labels = labels_conso)

# d'où le dictionnaire associé
# remarque : avec folium, on est vraiment libre que sur la couleur de l'intérieur de l'icône, donc on va fixer la couleur de l'extérieur sur du bleu
# et ne faire correspondre que l'intérieur du logo avec la légende de couleurs
dico_DPE_conso = {'A' : '#039033' , 'B' : '#51b016', 'C' : '#c8d200', 'D' :'#fcea26','E' : '#f8bb01' , 'F' : '#eb690b' , 'G' : '#e30c1c'}

#groupe pour le menu d'affichage
#DPE_GES_group = fm.FeatureGroup(name="DPE - Gaz à effet de serre").add_to(m)
#cluster
#cluster_DPE_GES = MarkerCluster().add_to(DPE_GES_group)

#même principe que précédemment pour la légende
colors_GES = ['#feeff4', '#d9c1db', '#c6a8cc', '#b793bf', '#9e75ad', '#82599b', '#6a418f']
labels_GES = ["A  (moins de 5)", 'B  (entre 6 et 10)', 'C  (entre 11 et 20)','D  (entre 21 et 35)','E  (entre 36 et 55)','F  (entre 56 et 80)', 'G  (plus de 80)']

#groupe pour le menu d'affichage
dico_DPE_GES = {'A' : '#feeff4' , 'B' : '#d9c1db', 'C' : '#c6a8cc', 'D' :'#b793bf','E' : '#9e75ad' , 'F' : '#82599b' , 'G' : '#6a418f'}


#m = add_categorical_legend(m,"DPE - Classes d'émissions de gaz à effet de serre <br> (en kg équivalent CO2 par m^2 par an)", colors = colors_GES, labels = labels_GES)


#de même, le dictionnaire associé
dico_DPE_GES = {'A' : '#feeff4' , 'B' : '#d9c1db', 'C' : '#c6a8cc', 'D' :'#b793bf','E' : '#9e75ad' , 'F' : '#82599b' , 'G' : '#6a418f'}

def surface_corr(surface):
    '''exprime la surface habitable sans chiffres après la virgule
    on s'en sert aussi pour la conso d'energie et les GES
    les entrées sont du type numpy.float64'''
    L = list(str(surface.tolist()))
    c = 0
    while L[c] != '.' :
        c += 1
    
    L = L[:c]
    return ''.join(L)

def if_nan(string):
    """
    si le str est un nan alors on renvoie le str vide'' 
    """
    if string.isna():
        return ''
    else:
        return string

for i in range(len(base_DPE)):
  data = base_DPE.loc[i]
  if data['consommation_energie_brut'] != 0.0 : #détecte les lignes uniquement DLE (et n'itère pas dessus)
    geocode = [data['latitude'], data['longitude']]

    #name_tip = non_breaking_spaces(str(data['numero_rue_dpe'])+str(data['nom_rue_dpe'])) 
    #ça met des nan quand y a pas 'numero_rue_dpe' et comme y a souvent pas le h
    name_tip = non_breaking_spaces(str(data['result_label']))
    surface_habitable = surface_corr(data['surface_habitable'])
    score = pourcentage(data['score'])

    # données sur la consommation énergétique

    classe_conso = data['classe_consommation_energie']
    couleur_conso = dico_DPE_conso[classe_conso]
    conso_energie = surface_corr(data['consommation_energie_brut'])
      
  # données sur les émissions de GES

    classe_GES = data['classe_estimation_ges']
    couleur_GES = dico_DPE_GES[classe_GES]
    emissions_GES = surface_corr(data['estimation_ges_brut'])

    fm.Marker(geocode, name = name_tip,
    popup=f"<p><strong>{name_tip}</strong></p><p>Surface&nbsphabitable&nbsp:&nbsp{surface_habitable}&nbspmètres&nbspcarrés</p><p><strong>Classe&nbspConsommation&nbsp:&nbsp</strong>{classe_conso}</strong><br>Consommation&nbspénergétique&nbsp:&nbsp{conso_energie}&nbspkWh&nbsppar&nbspan&nbsp(énergie&nbspprimaire)<p><strong>Classe&nbspEmissions&nbsp:&nbsp</strong>{classe_GES}</strong><br>Emission&nbspde&nbspgaz&nbspà&nbspeffet&nbspde&nbspserre&nbsp:&nbsp{emissions_GES}&nbspkg&nbspéquivalent&nbspCO2</p><p><strong><p><em>Fiable&nbspà&nbsp{score}&nbsp%</em></p>",tooltip=name_tip,icon = fm.Icon(color='white', icon_color = couleur_conso, icon = 'home', prefix= 'fa')).add_to(cluster_DPE_conso)

        #fm.Marker(geocode,
        #popup=f"<p><strong>{name_tip}</strong></p><p>Surface&nbsphabitable&nbsp:&nbsp{surface_habitable}&nbspmètres&nbspcarrés</p><p><strong>Classe&nbspEmissions&nbsp:&nbsp</strong>{classe_GES}</strong><p>Emission&nbspde&nbspgaz&nbspà&nbspeffet&nbspde&nbspserre&nbsp:&nbsp{emissions_GES}&nbspkg&nbspéquivalent&nbspCO2</p><p><strong><p><em>Fiable&nbspà&nbsp{score}&nbsp%</em></p>",tooltip=name_tip,icon = fm.Icon(color='blue', icon_color = couleur_GES, icon = 'home', prefix= 'fa')).add_to(cluster_DPE_GES)      
    

fm.LayerControl().add_to(m)
fm.plugins.Search(cluster_DPE_conso, search_label = "name", placeholder = "Rechercher un bâtiment (DPE)").add_to(m)
#fm.plugins.Search(cluster_DLE_all, search_label = "name", placeholder = "Rechercher un bâtiment (DLE)").add_to(m)

#sauvegarde dans un fichier html
m.save('../site/carte_projet.html')
