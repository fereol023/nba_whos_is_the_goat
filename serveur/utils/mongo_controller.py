from utils.connector import Connector
import pandas as pd

from utils.nba_api_controller import find_stats_by_season

class CareersController:
    def __init__(self):
        self.db = Connector().get_nba_db()
        self.collection = self.db['players_stats']

    def find_all(self):
        res = self.collection.find({}, {'_id':0, 'nba_id':0})
        return list(res)
                
    
    def find_all_numeric_and_names(self):
        res = self.collection.find({}, {'_id':0, 'nba_id':0, 'current_team':0, 'LEAGUE_ID':0, 'Team_ID':0})
        res = pd.DataFrame(res)
        res['career_duration'] = res.to_year.astype('int64[pyarrow]') - res.from_year.astype('int64[pyarrow]')
        res = res[[c for c in res.columns if c not in ['from_year', 'to_year']]]
        return res

    def find_names(self):
        res = pd.DataFrame(self.find_all())['full_name']
        return list(res)


class SeasonController:
    
    @staticmethod
    def find(player_name):
        return find_stats_by_season(player_name)