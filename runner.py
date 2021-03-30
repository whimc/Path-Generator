import mysql.connector
import sys
import os
from PIL import Image, ImageDraw
from configparser import ConfigParser
from threading import Thread, Lock
import argparse

import map_drawer
import imgur_uploader

mutex = Lock()

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

def generate_images(username, start_time: int, end_time: int, gen_empty=False):
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

    invalid = False
    for var, value in creds.items():
        if value is not None:
            continue
        creds[var] = parser.get('database', var, fallback=None)

        if not creds[var]:
            print(f'"{var}" is not set within "./config.ini"!')
            invalid = True

    if invalid:
        exit()

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

    print('\nGathering data:')
    print(f'\t{len(pos_data)} total positions')
    print(f'\t{len(block_data)} total blocks')
    print(f'\t{len(obs_data)} total observations')
    print('')

    draw_dict = map_drawer.draw_path_image(draw_dict, username, start_time, end_time,
                                pos_data, block_data, obs_data, gen_empty)

    img_map = { key:val for key, val in img_map.items() if
        key in draw_dict }

    if not os.path.exists('output'):
        os.mkdir('output')

    if not os.path.exists(os.path.join('output', username)):
        os.mkdir(os.path.join('output', username))

    if not os.path.exists(os.path.join('output', username, f'{start_time}-{end_time}')):
        os.mkdir(os.path.join('output', username, f'{start_time}-{end_time}'))

    if not img_map.keys():
        return

    print('\nSaving images:')
    threads = []
    for (name, img) in img_map.items():
        gen_path = os.path.join('output', f'{name}.png')
        spec_path = os.path.join('output', username, f'{start_time}-{end_time}', f'{name}.png')

        thread = Thread(target=save_image, args=(img, name, gen_path, spec_path))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print('')


def save_image(image, world_name, *paths):
    for path in paths:
        image.save(path)
    print(f'\tImage saved for {world_name}.')

def get_path_links(username, start_time, end_time, no_imgur=False,
        overwrite=False, gen_empty=False, *args, **kwargs):
    """Uploads path images to Imgur and returns json containing links to each image.

    Arguments:
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time

    Returns:
        json_str -- JSON object with links to generated images
    """

    for file_name in os.listdir('output'):
        path = os.path.join('output', file_name)
        if not os.path.isfile(path):
            continue
        os.remove(path)

    print(f'Generating for {username}: {start_time}-{end_time}')
    generate_images(username, start_time, end_time, gen_empty)

    # Skip uploading to imgur if they have have that option set
    if no_imgur:
        return None

    print('')

    path_name_dict = dict()
    for file_name in os.listdir('output'):
        path = os.path.join('output', file_name)
        if not os.path.isfile(path):
            continue
        img_name = f'{username}-{start_time}-{end_time}_{file_name}'
        path_name_dict[path] = img_name

    if not path_name_dict:
        print('There are no images to upload!')
        return None

    print('Uploading images to Imgur...')

    return imgur_uploader.upload_to_imgur(path_name_dict, overwrite)

def prompt_runner(**kwargs):
    """Runner for program using terminal-based input
    """
    kwargs['username'] = input('Player username: ')
    kwargs['start_time'] = int(input('Unix start-time: '))
    kwargs['end_time'] = int(input('Unix end-time: '))

    links = get_path_links(**kwargs)
    if not links:
        return

    print('\nLinks:')
    padding = len(max(links.keys(), key=len)) + 1
    for name, link in links.items():
        print(f'\t{name:<{padding}} -> {link}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-imgur', action='store_true', dest='no_imgur',
                        help='Do not upload the resulting images to Imgur.')
    parser.add_argument('-o', '--overwrite', action='store_true', dest='overwrite',
                        help='If the path image already exists on Imgur, overwrite it.')
    parser.add_argument('-e', '--generate-empty', action='store_true', dest='gen_empty',
                        help='Still generate a path image even if it has no actions on it.')

    options = vars(parser.parse_args())
    prompt_runner(**options)

    # get_path_links('Poi', 1570000000, 1582000000)
