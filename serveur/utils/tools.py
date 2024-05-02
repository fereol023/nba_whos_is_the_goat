from pyspark.sql.functions import udf
from pyspark.sql.types import MapType, StringType, ArrayType, IntegerType

from utils.nba_api_controller import fetch_regular_season_stats


fetch_stats = udf(fetch_regular_season_stats, MapType(StringType(), IntegerType()))

test = udf(lambda n: n.upper(), StringType())
