import mysql.connector
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import map_drawer

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

WORLD_NAMES = {
    'ColdMapViable': 39,
    'EarthBaseV3': 14,
    'HabitableStripV2': 51,
    'HotMap': 38,
    'JungleIslandEquator': 55,
    'NoMoonFinal_': 52,
    'TiltedM1Final': 43,
    'TiltedM3Final': 42
}

def fetch_position_data(cursor, username, start_time, end_time):
    """
    Fetches all position data for a user between two times.
    """

    global WORLD_NAMES
    map_in_query = '(' + (','.join(f"'{world}'" for world in WORLD_NAMES)) + ')'

    cursor.execute(
        "SELECT world AS world_name, x, y, z, time "
        "FROM dm_position "
        f"WHERE username = '{username}' "
        f"AND world IN {map_in_query} "
        "ORDER BY world, time ASC"
    )

    return sorted(cursor.fetchall(), key = lambda x: (x[0], x[4]))

def fetch_block_data(cursor, username, start_time, end_time):
    """
    Fetches all block data for a user between two times.
    """

    global WORLD_NAMES
    map_in_query = '(' + (','.join(f"'{wid}'" for wid in WORLD_NAMES.values())) + ')'

    cursor.execute(
        "SELECT ("
        " SELECT world FROM co_world WHERE id = wid) AS world_name, "
        " x, y, z, action "
        "FROM co_block as b "
        f"WHERE time BETWEEN {start_time} AND {end_time} "
        f"AND user = (SELECT rowid FROM co_user WHERE user = '{username}') "
        f"AND wid IN {map_in_query} "
        "ORDER BY time ASC"
    )

    # res = [entry for entry in cursor.fetchall() if entry[0] in WORLD_NAMES]
    # return sorted(res, key = lambda x: (x[0], x[4]))
    return cursor.fetchall()

def fetch_observation_data(cursor, username, start_time, end_time):
    """
    Fetches all observation data for a user between two times
    """

    global WORLD_NAMES
    map_in_query = '(' + (','.join(f"'{world}'" for world in WORLD_NAMES)) + ')'

    cursor.execute(
        "SELECT world AS world_name, x, y, z, observation "
        "FROM whimc_observations "
        f"WHERE name = '{username}' "
        f"AND time between {int(start_time) * 1000} AND {int(end_time) * 1000} "
        f"AND world IN {map_in_query} "
        "AND active = 1"
    )

    # res = [entry for entry in cursor.fetchall() if entry[0] in WORLD_NAMES]
    # return sorted(res, key = lambda x: (x[0], x[4]))
    return cursor.fetchall()

def get_path(username, start_time, end_time):

    global WORLD_NAMES

    draw_map = dict()
    img_map = dict()
    for world_name in WORLD_NAMES:
        try:
            img_file = Image.open(os.path.join('maps', f'{world_name}.png'))
            draw_map[world_name] = ImageDraw.Draw(img_file)
            img_map[world_name] = img_file
        except Exception:
            print(sys.exc_info()[0])

    mydb = mysql.connector.connect(**creds)
    cursor = mydb.cursor()

    pos_data = fetch_position_data(cursor, username, start_time, end_time)
    block_data = fetch_block_data(cursor, username, start_time, end_time)
    obs_data = fetch_observation_data(cursor, username, start_time, end_time)

    cursor.close()

    count = 0

    prev_world = pos_data[0][0]
    
    print(len(pos_data))
    print(block_data)
    print(obs_data)

    map_drawer.draw_observations(draw_map, obs_data)
    map_drawer.draw_blocks(draw_map, block_data)

    for (name, img) in img_map.items():
        img.save(os.path.join('output', f'{name}.png'))

get_path('Poi', '1570000000', '1582000000')