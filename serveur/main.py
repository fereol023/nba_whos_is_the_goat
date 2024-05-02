from utils.migration import *
from utils.mongo_controller import *
import uvicorn
from fastapi import FastAPI, HTTPException
#print(fetch_regular_season_stats('Tom Abernethy'))
from analysis import Analyzer

app = FastAPI()


@app.get('/')
def start():
    return "HELLO"


@app.get('/create_database/careers')
def create_db1():
    """fetch data for players careers stats and store to mongodb."""
    try:
        make_migration()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur while fetch-migrate from nba API.")
    
@app.get('/analysis/full_data')
def exec_global_data():
    try:
        return CareersController().find_all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur while performing loading data : {e}.")


@app.get('/analysis/data_tsne')
def exec_tsne():
    try:
        return Analyzer().tsne_reduction(n_comp=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur while performing TSNE algo : {e}.")

@app.get('/analysis/data_pca')
def exec_tsne():
    try:
        return Analyzer().pca_reduction(n_comp=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur while performing TSNE algo : {e}.")


@app.get('/analysis/player_names')
def exec_names():
    try:
        return CareersController().find_names()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur while fetching names : {e}.")

@app.get('/analysis/by_name/{p_name}')
def exec_by_name(p_name):
    """expose find stats by seasons by player name"""
    players = [u.lower() for u in CareersController().find_names()]
    try:
        p_name = str(p_name)
        if p_name.lower() not in players:
            return []
        return SeasonController.find(p_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur dans telechargement stats par saison : {e}")

if __name__=='__main__':
    #print(CareersController().get_unlabelled_numeric().head(5))
    #Analyzer().tsne_reduction()
    pass