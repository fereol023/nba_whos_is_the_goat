from pyspark.sql import SparkSession
from pyspark.sql import types as T
from utils.connector import *
from utils.nba_api_controller import *

def transform():
    
    spark = SparkSession.builder.appName("NBA DataViz") \
                .config("spark.mongodb.input.uri", "mongodb://localhost:27017") \
                .config("spark.mongodb.output.uri", "mongodb://localhost:27017") \
                .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
                .master("local") \
                .getOrCreate()

    #conf = Connector().get_config_collection('players_stats')
    #spark = SparkSession.builder.appName('NBA Dataviz').config('spark.mongodb.output.uri', conf).getOrCreate()
    #spark = SparkSession.builder.appName('NBA Dataviz').getOrCreate()
    
    try:
        player_infos = load_players_infos()

        # add stats
        #player_infos['career_stats'] = player_infos['DISPLAY_FIRST_LAST'].apply(lambda n: fetch_regular_season_stats(n)) 

        df = spark.createDataFrame(player_infos)
        df1 = df.select(df.PERSON_ID.alias('nba_id'), 
                        df.DISPLAY_FIRST_LAST.alias('full_name'),
                        df.FROM_YEAR.alias('from_year'),
                        df.TO_YEAR.alias('to_year'),
                        df.TEAM_NAME.alias('current_team'))
        #df1 = df1.sample(False, 0.005)
        #df1.show()
        #p_names = [row['full_name'] for row in df1.select('full_name').collect()]
        p_ids = set([row['nba_id'] for row in df1.select('nba_id').collect()])
        #print(p_names)
        #stats_data = fetch_all_regular_season_stats(p_names)
        stats_data_v2 = fetch_all_regular_season_stats_v2(p_ids)
        #stats_df = spark.createDataFrame(stats_data, ['full_name', 'stats'])
        v2_cols = [
            'nba_id', 'LEAGUE_ID', 'Team_ID', 'GP', 'GS', 
            'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A',
            'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 
            'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'
        ]
        #stats_df_v2 = spark.createDataFrame(stats_data_v2, v2_cols)
        schema = T.StructType([
        T.StructField('nba_id', T.IntegerType(), True),
        T.StructField('LEAGUE_ID', T.StringType(), True),
        T.StructField('Team_ID', T.IntegerType(), True),
        T.StructField('GP', T.IntegerType(), True),
        T.StructField('GS', T.IntegerType(), True),
        T.StructField('MIN', T.FloatType(), True),
        T.StructField('FGM', T.IntegerType(), True),
        T.StructField('FGA', T.IntegerType(), True),
        T.StructField('FG_PCT', T.FloatType(), True),
        T.StructField('FG3M', T.IntegerType(), True),
        T.StructField('FG3A', T.IntegerType(), True),
        T.StructField('FG3_PCT', T.FloatType(), True),
        T.StructField('FTM', T.IntegerType(), True),
        T.StructField('FTA', T.IntegerType(), True),
        T.StructField('FT_PCT', T.FloatType(), True),
        T.StructField('OREB', T.IntegerType(), True),
        T.StructField('DREB', T.IntegerType(), True),
        T.StructField('REB', T.IntegerType(), True),
        T.StructField('AST', T.IntegerType(), True),
        T.StructField('STL', T.IntegerType(), True),
        T.StructField('BLK', T.IntegerType(), True),
        T.StructField('TOV', T.IntegerType(), True),
        T.StructField('PF', T.IntegerType(), True),
        T.StructField('PTS', T.IntegerType(), True)
        ])
        stats_df_v2 = spark.createDataFrame(stats_data_v2, schema=schema)
        stats_df_v2.limit(3).show()

        df2 = df1.join(other=stats_df_v2, on=['nba_id'], how='inner')
        df2.limit(3).show()
        return df2
    except Exception as e:
        print(f"erreur transformation {e}")


def ingest(D):
    D.write \
        .format("mongo") \
        .mode("append") \
        .option("database", "nba_db") \
        .option("collection", "players_stats") \
        .save()


def make_migration():
    res = transform()
    ingest(res)