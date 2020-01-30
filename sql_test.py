import mysql.connector
import os
import sys
from PIL import Image, ImageDraw, ImageFont

creds = {
    'host': '96.127.169.218',
    'database': 'mc115627',
    'user': 'mc115627',
    'password': 'd149e703df',
    'use_pure': True,
    'charset': 'utf8',
}
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

username = 'Poi'
start_time = '1570000000'
end_time = '1580000000'
world_names = [
    'ColdMapViable',
    'EarthBaseV3',
    'HabitableStripV2',
    'HotMap',
    'JungleIslandEquator',
    'NoMoonFinal_',
    'TiltedM1Final',
    'TiltedM3Final'
]

# map_in_query = '(' + (','.join(f"'{string}'" for string in world_names)) + ')'

# mydb = mysql.connector.connect(**creds)
# cursor = mydb.cursor()

# # Block interactions
# cursor.execute(
#     "SELECT world AS world_name, x, y, z, time "
#     "FROM dm_position "
#     f"WHERE username = '{username}' "
#     f"AND world IN {map_in_query} "
#     "ORDER BY time ASC"
# )

# pos_data = cursor.fetchall()
# # for entry in pos_data:
# #     print(entry)
# print(f'{len(pos_data)} position entries')


# # Positions
# cursor.execute(
#     "SELECT ("
#     " SELECT world FROM co_world WHERE id = wid) AS world_name, "
#     " x, y, z, time "
#     "FROM co_block as b "
#     f"WHERE time BETWEEN {start_time} AND {end_time} "
#     f"AND user = (SELECT rowid FROM co_user WHERE user = '{username}') "
#     "ORDER BY time ASC"
# )

# block_data = cursor.fetchall()
# # for entry in block_data:
# #     print(entry)
# print(f'{len(block_data)} block entries')


# # Observations
# cursor.execute(
#     "SELECT world AS world_name, x, y, z, observation "
#     "FROM whimc_observations "
#     f"WHERE name = '{username}' "
#     "AND active = 1"
# )

# obs_data = cursor.fetchall()
# # for entry in obs_data:
# #     print(entry)
# print(f'{len(obs_data)} observation entries')


draw_map = {}
for world_name in world_names:
    try:
        img_file = Image.open(os.path.join('maps', f'{world_name}.png'))
        draw_map[world_name] = ImageDraw.Draw(img_file)
    except Exception:
        print(sys.exc_info()[0])


for (world_name, x, y, z, time) in pos_data:
    pass

for (world_name, x, y, z, time) in block_data:
    pass

for (world_name, x, y, z, observation) in obs_data:
    pass