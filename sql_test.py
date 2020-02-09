import mysql.connector
import os
import sys
from PIL import Image, ImageDraw, ImageFont

creds = {
    'host': None,
    'database': None,
    'user': None,
    'password': None,
    'use_pure': True,
    'charset': 'utf8',
}

for var in creds.keys():
    if creds[var] is not None:
        continue
    env_var = f'MAPGEN_{var.upper()}'
    if env_var in os.environ:
        creds[var] = os.environ[env_var]
        print(f'{env_var}={creds[var]}')
    else:
        print(f'* {env_var} is not set as an environment variable!')

if None in creds.values():
    exit()

WORLD_NAMES = [
    'ColdMapViable',
    'EarthBaseV3',
    'HabitableStripV2',
    'HotMap',
    'JungleIslandEquator',
    'NoMoonFinal_',
    'TiltedM1Final',
    'TiltedM3Final'
]

def fetch_position_data(cursor, username, start_time, end_time):
    """
    Fetches all position data for a user between two times.
    """

    global WORLD_NAMES
    # map_in_query = '(' + (','.join(f"'{world}'" for world in WORLD_NAMES)) + ')'

    cursor.execute(
        "SELECT world AS world_name, x, y, z, time "
        "FROM dm_position "
        f"WHERE username = '{username}' "
        # f"AND world IN {map_in_query} "
        "ORDER BY time ASC"
    )

    res = [entry for entry in cursor.fetchall() if entry[0] in WORLD_NAMES]
    return sorted(res, key = lambda x: (x[0], x[4]))

def fetch_block_data(cursor, username, start_time, end_time):
    """
    Fetches all block data for a user between two times.
    """

    global WORLD_NAMES

    cursor.execute(
        "SELECT ("
        " SELECT world FROM co_world WHERE id = wid) AS world_name, "
        " x, y, z, time "
        "FROM co_block as b "
        f"WHERE time BETWEEN {start_time} AND {end_time} "
        f"AND user = (SELECT rowid FROM co_user WHERE user = '{username}') "
        "ORDER BY time ASC"
    )

    res = [entry for entry in cursor.fetchall() if entry[0] in WORLD_NAMES]
    return sorted(res, key = lambda x: (x[0], x[4]))

def fetch_observation_data(cursor, username, start_time, end_time):
    """
    Fetches all observation data for a user between two times
    """

    global WORLD_NAMES

    cursor.execute(
        "SELECT world AS world_name, x, y, z, observation "
        "FROM whimc_observations "
        f"WHERE name = '{username}' "
        "AND active = 1"
    )

    res = [entry for entry in cursor.fetchall() if entry[0] in WORLD_NAMES]
    return sorted(res, key = lambda x: (x[0], x[4]))

def get_path(username, start_time, end_time):

    global WORLD_NAMES

    draw_map = dict()
    for world_name in WORLD_NAMES:
        try:
            img_file = Image.open(os.path.join('maps', f'{world_name}.png'))
            draw_map[world_name] = ImageDraw.Draw(img_file)
        except Exception:
            print(sys.exc_info()[0])

    mydb = mysql.connector.connect(**creds)
    cursor = mydb.cursor()

    pos_data = fetch_position_data(cursor, username, start_time, end_time)
    block_data = fetch_block_data(cursor, username, start_time, end_time)
    obs_data = fetch_observation_data(cursor, username, start_time, end_time)

    count = 0

    prev_world = pos_data[0][0]
    for (world_name, x, y, z, time) in pos_data:
        # print(world_name, x, y, z, time)
        count+=1

    for (world_name, x, y, z, time) in block_data:
        # print(world_name, x, y, z, time)
        count+=1

    for (world_name, x, y, z, observation) in obs_data:
        # print(world_name, x, y, z, observation)
        count+=1

    print(count)

get_path('Poi', '1570000000', '1580000000')