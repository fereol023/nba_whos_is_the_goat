from env import *
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt 
import numpy as np
#import plotly.express as px
import seaborn as sns
from PIL import Image
from utils.graph_ import *
from utils.data import superstars, lieutenants
import plotly.express as px

st.set_option('deprecation.showPyplotGlobalUse', False)
#st.set_page_config(layout="wide")

# ----------------------------
header_cols = st.columns(3, gap='large')

with header_cols[1]:
    st.header('Statistiques des joueurs')

with header_cols[0]:
    logo = Image.open('images/logo_nba.jpeg')
    #logo.resize((100,50))
    st.image(logo)

# -----------------------------
legend_ = {"GP": "The total amount of games played by a player or a team.",
           "GS": "The total amount of games started by a player or a team.",
           "MIN": "The total amount of minutes played by a player or a team.",
           "FGM": "The total amount of shots made from the field.",
           "FGA": "The total amount of shots attempted from the field.",
           "FG_PCT": "The percentage of shots made compared to the shots attempted.",
           "FG3M": "The total amount of 3PTS shots made from the field.",
           "FG3A":  "The total amount of 3PTS shots attempted from the field.",
           "FG3_PCT":  "The percentage of 3PTS made compared to the shots attempted.",
           "FTM": "The total amount of free throws made.",
           "FTA": "The total amount of free throws attempted.",
           "FT_PCT": "The percentage of shots made compared to the shots attempted.",
           "OREB": "The total amount of offensive rebounds grabbed.",
           "DREB": "The total amount of defensive rebounds grabbed.",
           "REB": "OFFENSIVE REB + DEFENSIVE REB",
           "AST": "The total amount of assists made (a pass made before a teammate’s shot made).",
           "STL": "The total amount of balls stolen during the defense.",
           "BLK": "The total amount of blocked shots during the defense.",
           "TOV": "The total amount of balls lost during the offense.",
           "PF": "The total amount of fouls committed.",
           "PTS": "The total amount of points made."}

st.text('')
st.text('')
st.text('Definition des termes techniques')
st.write(legend_)

# ---------------------
data = pd.DataFrame(requests.get(f'http://{server_url}/analysis/full_data').json())
st.text('')
st.text("Aperçu des données dans la collection player_stats")
st.write(data.head(2))


# -----------------------------
lib_metrique_global=st.selectbox(label='Choix métrique', options=tuple([f"{k} - {v}" for k,v in legend_.items()]))
metrique_global = lib_metrique_global.split(' - ')[0]

cols = st.columns(2)
with cols[0]:
    # chercher un joueur
    """Choisir ici le joueur dont vous voulez voir les infos"""
    choix_joueur_global = st.text_input('Qui ?', placeholder='exple. Tony Parker', value=None)
    if choix_joueur_global not in data['full_name'].values:
        st.warning('Oh oh joueur non disponible..', icon="⚠️")
    else: 
        ligne_joueur_global = data.loc[data.full_name==choix_joueur_global]
        if len(ligne_joueur_global)==1:
            stat_joueur_global = ligne_joueur_global.get(metrique_global).values[0]
            active = True if int(ligne_joueur_global.get('to_year').values[0]) >= 2023 else False

            resume_j = f"Son {lib_metrique_global.split(' - ')[1]} s'élève à {stat_joueur_global}."            
            if not active:
                resume_i = f"{choix_joueur_global} a joué entre {ligne_joueur_global.get('from_year').values[0]} et {ligne_joueur_global.get('to_year').values[0]} ."
            else :
                resume_i = f"{choix_joueur_global} joue depuis {2024-int(ligne_joueur_global.get('from_year').values[0])} ans. Il a commencé sa carrière en {ligne_joueur_global.get('from_year').values[0]}. Il joue actuellement pour l'équipe des {ligne_joueur_global.get('current_team').values[0]}. "
            
            st.text('')
            text=f"{resume_i}\n{resume_j}"
            st.write(text)
        else:
            st.warning("Oh oh qq chose s'est mal passé..", icon="⚠️")

with cols[1]:
    g = st.radio("Type de graphique", ("Histogramme", "Densité de proba", "F. répartition"))

    pas = lambda x: np.linspace(start=0, stop=max(x), num=20)
    if metrique_global:
        try:
            plt.figure(figsize=None)
            X = data[metrique_global.upper()].values
            if g=="Histogramme":
                sns.histplot(X, bins=pas(X))
                plt.title(f'Histogramme : pas=20')
                st.pyplot()
            elif g=="Densité de proba":
                sns.kdeplot(X, common_norm=False)
                plt.title('Densité de probabilité')
                st.pyplot()
            else:
                sns.displot(X, kind='ecdf')
                plt.title('Densité de probabilité')
                st.pyplot()
        except:
            st.warning("Qlq chose s'est mal passé")
            raise

# -----------------
top = st.radio(' ', ('CLASSEMENT TOP 10', 'CLASSEMENT TOP 5'), horizontal=True)
top = top.split(' ')[-1]
k = int(top) - 1

top_scope = (
                "Nombre de points marqués",
                "Nombre de rebonds total",
                "Contribution défensive (STL+BLK)",
                "Capacité à créer des opprotunités pour son équipe",
                "Efficacité globale au tir"
            )
choix_top_scope = st.selectbox('METRIQUE', top_scope, placeholder='Choisir une stat..')

if choix_top_scope == "Nombre de points marqués":
    y = 'PTS'
elif choix_top_scope == "Nombre de rebonds total":
    y = 'REB'
elif choix_top_scope == "Contribution défensive (STL+BLK)":
    y = 'STL'
elif choix_top_scope == "Capacité à créer des opprotunités pour son équipe":
    y = 'AST'
elif choix_top_scope == "Efficacité globale au tir":
    y = 'FG_PCT'

data['ratio'] = round(data[y] / data['GP'], 3)

sub_data = data.sort_values(by=[y, 'ratio'], ascending=False).reset_index().loc[:k,['full_name', y, 'ratio']]


plt.figure(figsize=(10,6))
fig, ax1 = plt.subplots()
sns.barplot(x='full_name', y=y, data=sub_data, ax=ax1, color='skyblue')
plt.xticks(rotation=45)
ax1.set_ylabel('Stat au global')
ax2 = ax1.twinx()
sns.lineplot(x='full_name', y='ratio', data=sub_data, ax=ax2, color='coral', marker='o')
ax2.set_ylabel('Moyenne par matchs joués')
ax2.tick_params(axis='y', colors='darkred')
st.pyplot()

# -----------------
tsne = requests.get(f'http://{server_url}/analysis/data_tsne').json()
pca = requests.get(f'http://{server_url}/analysis/data_pca').json()

algo_clustering = st.radio("Choisir l'algo de clustering à utiliser :", ("TSNE", "PCA"))

st.write('Info : La carte des joueurs permet de visualiser le positionnement de quelques joueurs exceptionnels (franchise players, lieutenants) par rapport au reste.')
if st.button('Carte des joueurs'):
    if algo_clustering=='TSNE':
        #plt.figure(figsize=(10,3))
        plt.title('TSNE joueurs.')
        X = np.array(tsne['weights'])
        X = (X - np.mean(X, axis=0))/np.std(X, axis=0)
        X = pd.DataFrame(X, columns=['axe1', 'axe2']) #new
        
        y = list(map(lambda i: 'superstars' if i in superstars else 'bons seconds' if i in lieutenants else 'autres', tsne['names']))
        #y = pd.Series(tsne['names']) # old
        #fig_, ax = plot_repr(X=X, y=y, title='TSNE viz') # old
        X['categ'] = y
        sns.scatterplot(data=X, x='axe1', y='axe2', hue='categ', s=10)
        plt.savefig('tsne.png')
        st.pyplot()
    else:
        plt.title('PCA joueurs.')
        X = np.array(pca['weights'])
        X = pd.DataFrame(X, columns=['axe1', 'axe2']).reset_index(drop=True)
        print(X.tail())

        y = list(map(lambda i: 'superstars' if i in superstars else 'bons seconds' if i in lieutenants else 'autres', pca['names']))
        #y = pd.Series(y).reset_index(drop=True)
        X['categ'] = y
        #print(y)
        assert len(y)==len(X)
        #fig_, ax = plot_repr(X=X, y=y, title='PCA viz')
        # fig_ = px.scatter(X, color=y)
        #print(X.columns)
        sns.scatterplot(data=X, x='axe1', y='axe2', hue='categ', s=10)
        plt.savefig('pca.png')
        st.pyplot()

# ------------- lebron vs jordan
"""COMPARAISON 1V1"""
comp_cols = st.columns(2)

with comp_cols[0]:
    p1_name = st.text_input('qui ?', value=None)
    if p1_name:
        player1 = pd.DataFrame(requests.get(f'http://{server_url}/analysis/by_name/{p1_name}').json())
        player1.insert(loc=0, column='name', value=p1_name)
        player1.insert(loc=1, column='year_k', value=[f'year_{i}' for i in player1.index+1])
        st.write(player1.head(3))


with comp_cols[1]:
    p2_name = st.text_input('vs qui ?')
    if p2_name:
        player2 = pd.DataFrame(requests.get(f'http://{server_url}/analysis/by_name/{p2_name}').json())
        player2.insert(loc=0, column='name', value=p2_name)
        player2.insert(loc=0, column='year_k', value=[f'year_{i}' for i in player2.index+1])
        st.write(player2.head(3))


if p1_name and p2_name:
    comp_df = pd.concat([player1, player2])
    f"Nombre de saisons"
    nb_seasons = comp_df[['name', 'SEASON_ID']].groupby('name').size()
    fig, ax = plt.subplots()
    sns.barplot(nb_seasons)
    ax.set_ylabel('Nombre de saisons jouées')
    plt.yticks(ticks=np.linspace(start=0, stop=24, num=3))
    st.pyplot()

    f"Le nombre de points moyen par match par saison jouée"
    # PTS:  lineplot two dim avec year_k en abscisse
    comp_df['PTS/GP'] = comp_df['PTS']/comp_df['GP']
    sns.lineplot(data=comp_df, hue='name', x='year_k', y='PTS/GP')
    ax.set_xlabel('Année de carrière')
    ax.set_ylabel('Points en moyenne par match')
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot()

    f"Efficacité moyenne de tir de chaque joueur"
    # FG_PCT:  lineplot two dim avec year_k en abscisse
    sns.lineplot(data=comp_df, hue='name', x='year_k', y='FG_PCT')
    ax.set_xlabel('Année de carrière')
    ax.set_ylabel('%Succès shoots')
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot()

    f"La contribution défensive de chaque joueur"
    # STOCKS : lineplot two dim avec year_k en abscisse
    comp_df['STOCKS'] = comp_df['BLK'] + comp_df['STL']
    sns.lineplot(data=comp_df, hue='name', x='year_k', y='STOCKS')
    ax.set_xlabel('Année de carrière')
    ax.set_ylabel('STL + BLK')
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot()

    f"Quelle est la capacité de chaque joueur à créer des opportunités pour son équipe (assists) en moyenne par match ?"
    # AST
    comp_df['AST/GP'] = comp_df['AST']/comp_df['GP']
    sns.lineplot(data=comp_df, hue='name', x='year_k', y='AST/GP')
    ax.set_xlabel('Année de carrière')
    ax.set_ylabel('Assists en moyenne par match')
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot()
    # 

    lebron_jordan = [p1_name.lower(), p2_name.lower()]
    if all([n in ['lebron james', 'michael jordan'] for n in lebron_jordan]):
        comp=f"""
        LEBRON VS JORDAN : résultats

        --- INDIVIDUELLEMENT ---

        1. LEBRON joue plus de saisons que JORDAN (21 vs 15), donc au niveau des stats en absolu, il bat JORDAN. Par exemple le nombre de points total ( > 40000).

        La comparaison des stats en absolu pourrait être biaisé par la durée de la carrière : on comparera donc sur la moyenne par match joué.

        2. Parlant de PTS/GP JORDAN est largement devant LEBRON (SAUF LORS DE SES 2 DERNIERES SAISONS) : L'AGE DEFAVORISE JORDAN.

        3. En plus, la précision de JORDAN a une tendance à la baisse (de 54% à 42% au plus bas) alors que celle de LEBRON monte et converge vers 52% : L'AGE DEFAVORISE JORDAN.

        -> Conclusion partielle : 
        
        A CE NIVEAU, ON VOIT QUE JORDAN ETAIT GLOBALEMENT MEILLEUR QUE LEBRON LES 12 PREMIERES ANNEES DE SA CARRIERE - MAIS IL ETAIT DE MOINS EN MOINS EFFICACE AVEC LES ANNEES QUI PASSENT. 
        LEBRON S'AMELIORE AVEC L'ANCIENNETE ET RESTE MEILLEUR QUE JORDAN AVEC LE TEMPS.

        --- JEU D'EQUIPE ---

        4. STOCKS décroissant pour les 2 : MOINS DE CONTRIBUTION DEFENSIVE AVEC L'AGE. 
                
        5. LEBRON dépasse JORDAN en passes décisives, donc JORDAN gardait plus le ballon :
            (relation avec 2) le jeu était centré sur JORDAN donc il marquait beaucoup plus.
            (relation avec 3) il gardait beaucoup la balle mais sa précison se dégradait.

        LEBRON : AMILORATION + CONSTANCE + IMPACT DE L'AGE MOINS IMPORTANT + BON EQUIPIER  
        MICHAEL : BEAUCOUP DE QUALITE DANS SES DEBUTS MAIS DEGRADATION AU FIL DU TEMPS + EQUIPIER MOINS BON QUE LEBRON

        QUI EST LE MEILLEUR ?
        """
        st.write(comp)