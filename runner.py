import mysql.connector
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from configparser import ConfigParser

import map_drawer
import imgur_uploader


def get_envvar_or_secret(path):
    """Grabs a variable from environment variables or `secrets.py`
    
    Arguments:
        path {str} -- The name of the variable to grab
    
    Returns:
        str -- The value of the variable or None if it does not exist
    """
    if path in os.environ:
        return os.environ[path]
    if path in vars(secrets) and vars(secrets)[path]:
        return vars(secrets)[path]
    
    print(f'* {path} is not set as an environment variable or within `secrets.py`!')
    return None

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

def fetch_position_data(cursor, username, start_time: int, end_time: int):
    """Fetches all position data for a user between two times.
    
    Arguments:
        cursor {MySQLCursor} -- Cursor to execute query on
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    
    Returns:
        list() : (world_name, x, y, z, time) -- List of tuples containing queried information
    """

    global WORLD_NAMES
    map_in_query = '(' + (','.join(f"'{world}'" for world in WORLD_NAMES)) + ')'

    cursor.execute(
        "SELECT world AS world_name, x, y, z, time "
        "FROM dm_position "
        f"WHERE username = '{username}' "
        f"AND time BETWEEN {start_time} AND {end_time} "
        f"AND world IN {map_in_query} "
        "ORDER BY world, time ASC"
    )

    return sorted(cursor.fetchall(), key = lambda x: (x[0], x[4]))

def fetch_block_data(cursor, username, start_time: int, end_time: int):
    """Fetches all block data for a user between two times.
    `action` corresponds to 0 if block was placed and 1 if block was broken.
    
    Arguments:
        cursor {MySQLCursor} -- Cursor to execute query on
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    
    Returns:
        list() : (world_name, x, y, z, action) -- List of tuples containing queried information
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

    return cursor.fetchall()

def fetch_observation_data(cursor, username, start_time: int, end_time: int):
    """Fetches all observation data for a user between two times.
    
    Arguments:
        cursor {MySQLCursor} -- Cursor to execute query on
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    
    Returns:
        list() : (world_name, x, y, z, observation) -- List of tuples containing queried information
    """

    global WORLD_NAMES
    map_in_query = '(' + (','.join(f"'{world}'" for world in WORLD_NAMES)) + ')'

    cursor.execute(
        "SELECT world AS world_name, x, y, z, observation "
        "FROM whimc_observations "
        f"WHERE name = '{username}' "
        f"AND time between {start_time * 1000} AND {end_time * 1000} "
        f"AND world IN {map_in_query} "
        "AND active = 1"
    )

    return cursor.fetchall()

def generate_images(username, start_time: int, end_time: int):
    """Generate path images for all worlds for the given user between `start_time` and `end_time`.
    Saves path images with `output/`.
    
    Arguments:
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    """

    creds = {
        'host': None,
        'database': None,
        'user': None,
        'password': None,
        'use_pure': True,
        'charset': 'utf8',
    }

    parser = ConfigParser()
    parser.read('config.ini')

    for var, value in creds.items():
        if value is not None:
            continue
        creds[var] = parser.get('database', var, fallback=None)
    
        if not creds[var]:
            print(f'`{var}` is not set in `config.ini`!')

    if None in creds.values():
        exit()

    global WORLD_NAMES

    draw_dict = dict()
    img_map = dict()
    for world_name in WORLD_NAMES:
        try:
            img_file = Image.open(os.path.join('maps', f'{world_name}.png'))
            with_footer = Image.new('RGB', (img_file.width, img_file.height + 200),
                            color=(230, 230, 230))
            with_footer.paste(img_file)

            draw_dict[world_name] = ImageDraw.Draw(with_footer)
            img_map[world_name] = with_footer
        except Exception:
            print(sys.exc_info()[0])

    mydb = mysql.connector.connect(**creds)
    cursor = mydb.cursor()

    pos_data = fetch_position_data(cursor, username, start_time, end_time)
    block_data = fetch_block_data(cursor, username, start_time, end_time)
    obs_data = fetch_observation_data(cursor, username, start_time, end_time)

    cursor.close()

    print(len(pos_data), 'positions')
    print(len(block_data), 'blocks')
    print(len(obs_data), 'observations')

    map_drawer.draw_path_image(draw_dict, username, start_time, end_time, 
                                pos_data, block_data, obs_data)

    if not os.path.exists('output'):
        os.mkdir('output')
        
    if not os.path.exists(os.path.join('output', username)):
        os.mkdir(os.path.join('output', username))

    if not os.path.exists(os.path.join('output', username, f'{start_time}-{end_time}')):
        os.mkdir(os.path.join('output', username, f'{start_time}-{end_time}'))

    for (name, img) in img_map.items():
        img.save(os.path.join('output', f'{name}.png'))
        img.save(os.path.join('output', username, f'{start_time}-{end_time}', f'{name}.png'))


def get_path_links(username, start_time: int, end_time: int):
    """Uploads path images to Imgur and returns json containing links to each image.
    
    Arguments:
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    
    Returns:
        json_str -- JSON object with links to generated images
    """

    generate_images(username, start_time, end_time)

    path_name_dict = dict()
    for file_name in os.listdir('output'):
        path = os.path.join('output', file_name)
        if not os.path.isfile(path):
            continue
        img_name = f'{username}-{start_time}-{end_time}_{file_name}'
        path_name_dict[path] = img_name

    links = imgur_uploader.upload_to_imgur(path_name_dict)
    return links

def prompt_runner():
    """Runner for program using terminal-based input
    """
    username = input('Player username: ')
    start_time = int(input('Unix start-time: '))
    end_time = int(input('Unix end-time: '))
    links = get_path_links(username, start_time, end_time)
    print(links)

# prompt_runner()
# get_path_links('Poi', 1570000000, 1582000000)