from pymongo import MongoClient
from config.env import * 

class Connector:
    def __init__(self):
        self.host = mongo_infos.get('host', None)
        self.port = mongo_infos.get('port', None)
        self.db_name = mongo_infos.get('db_name', None)
        self.path = f'mongodb://{self.host}:{self.port}/'

    def get_pyspark_config(self, collection_name): # old
        if self.host and self.port and self.db_name:
            return f'mongodb://{self.host}:{self.port}/{self.db_name}.{collection_name}'
        else:
            raise Exception('Error while loading config')
        
    def get_nba_db(self):
        """Retourne la db stockée sur mongo."""
        try:
            assert self.host and self.port and self.db_name
            client = MongoClient(self.path)
            return client[self.db_name]
        except:
            raise Exception('Error Connector().get_nba_db() while loading config')