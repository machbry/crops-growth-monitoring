from pathlib import Path

import pandas as pd
import geopandas as gpd

from shapely import wkt
from sqlalchemy import create_engine
from psycopg2.errors import UniqueViolation

from cgm.constants import SRID, CGM_POSTGRES_DB_URL
from cgm.logger import get_logger

log = get_logger()


columns_map = {"ID_PARCEL_2022": "id_parcel",
               "CODE_CULTU_2022": "code_cultu",
               "geometry": "geometry"}

sampled_rpg_data_folder = Path(__file__).parents[2] / "sampled_rpg_data"
tournesol_csv_path = sampled_rpg_data_folder / 'tournesol.csv'
maize_csv_path = sampled_rpg_data_folder / 'maize.csv'

engine = create_engine(CGM_POSTGRES_DB_URL, echo=False)

# load sample data from csv
tournesol_df = pd.read_csv(tournesol_csv_path)
maize_df = pd.read_csv(maize_csv_path)
rpg_data = pd.concat([tournesol_df, maize_df])
log.info("Data successfully loaded from CSVs : %s and %s", tournesol_csv_path, maize_csv_path)

# load geometry
rpg_data['geometry'] = rpg_data['geometry'].apply(wkt.loads)

# transform to geo dataframe and change crs
rpg_gdf = gpd.GeoDataFrame(rpg_data, crs='epsg:2154').to_crs(epsg=SRID)

# rename and select wanted columns
rpg_gdf = rpg_gdf.rename(columns=columns_map)[list(columns_map.values())]

# store in postgre db
try:
    rpg_gdf.to_postgis("rpg", con=engine, if_exists="append", index=False)
    log.info("Data successfully loaded in postgres database")
except UniqueViolation:
    log.warning("Data already loaded in postgres database")
