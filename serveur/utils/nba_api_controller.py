from nba_api.stats.endpoints import playercareerstats, commonallplayers
from nba_api.stats.static import players

    
def load_players_infos(format_pandas=True):
    """Retourne plusieurs infos dont le nom complet et le player_id."""
    if format_pandas:
        return commonallplayers.CommonAllPlayers(is_only_current_season=0).get_data_frames()[0]
    return  commonallplayers.CommonAllPlayers(is_only_current_season=0).get_dict()
    

def get_player_infos_by_full_name(n_):
    """Retourne plusieurs infos dont le player id."""
    res = players.find_players_by_full_name(n_)
    if res:
        # force le res sur le premier : ! à voir
        return res[0]

def get_player_id_by_full_name(n):
    return get_player_infos_by_full_name(n)['id']


# https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/examples.md


def int_caster(x):
    try:
        return int(x)
    except:
        return -1

def fetch_one_regular_season_stats(player_name=''):
    """utilise le player name pour query les stats du joueur."""
    
    res = {'PLAYER_ID': -1, 'LEAGUE_ID': -1, 'Team_ID': -1, 'GP': -1, 'GS': -1, 
                'MIN': -1, 'FGM': -1, 'FGA': -1, 'FG_PCT': -1, 'FG3M': -1, 'FG3A': -1,
                'FG3_PCT': -1, 'FTM': -1, 'FTA': -1, 'FT_PCT': -1, 'OREB': -1, 'DREB': -1, 
                'REB': -1, 'AST': -1, 'STL': -1, 'BLK': -1, 'TOV': -1, 'PF': -1, 'PTS': -1}
    try:
        if player_name:
            player_id = get_player_id_by_full_name(player_name)
        
        career_stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=30)
        # valeur si correspondance non trouvée pour éviter de faire crash l'udf
        # FAIRE JOINTURE DES 2 TABLES PAR PLAYER ID JOINTURE INTERNE
        
        data = career_stats.career_totals_regular_season.get_dict()
        if data['headers'] and isinstance(data['data'][0], list) and len(data['data'][0]>0):
            data_headers = data['headers']
            data_values = data['data'][0]
            data_ = {k: int_caster(v) for k,v in list(zip(data_headers, data_values))}
            res = data_
        return res 
    except Exception as e: 
        return res


def fetch_all_regular_season_stats(player_names=None):
    res = []
    if player_names is not None:
        for name in player_names:
            try:
                res.append((name, fetch_one_regular_season_stats(name)))
            except:
                pass
    return res

def fetch_all_regular_season_stats_v2(player_ids=None):
    res = []
    if player_ids is not None:
        print(f"start fetching data for {len(player_ids)} players..")
        for id in player_ids:
            #print(f'player id {id}')
            try:
                career_stats = playercareerstats.PlayerCareerStats(player_id=id, timeout=30)
                data = career_stats.career_totals_regular_season.get_dict()
                #print(data)
                if isinstance(data['data'][0], list) and len(data['data'][0])>0:
                    data_values = tuple(data['data'][0])
                    if len(data_values) == 24:
                        res.append(data_values)
            except:
                pass
    return res

from pyspark.sql.functions import udf
from pyspark.sql.types import MapType, StringType, ArrayType, IntegerType

#fetch_stats = udf(fetch_regular_season_stats, MapType(StringType(), StringType()))

test = udf(lambda n: n.upper(), StringType())



def find_stats_by_season(name=None):
    if name:
        id_ = get_player_id_by_full_name(name)
        if id_ is not None:
            res = playercareerstats.PlayerCareerStats(player_id=id_).get_normalized_dict()['SeasonTotalsRegularSeason']
            return list(res)
        else:
            return []

