import json
import os
from typing import List
from pathgenerator.models.world import World

PATH = 'config.json'

# Make sure the config exists
if not os.path.exists(PATH):
    exit(f"{PATH} not found!")

# Load the config from the JSON file
with open(PATH, 'r') as file:
    _config = json.load(file)

def get(section, key, fallback=None):
    """Get a value from a section of the config"""
    return _config.get(section).get(key, fallback)

def get_dict(section, *keys):
    """Get a dictionary of key-value pairs given a list of keys"""
    return { key : get(section, key) for key in keys }

def set_multi(section, *items):
    """Sets multiple key-value tuples in the config"""
    for key, value in items:
        _config[section][key] = value
    with open(PATH, 'w') as file:
        json.dump(_config, file, indent=4)

def set(section, key, value):
    """Set a key-value pair in the config"""
    set_multi(section, (key, value))

def validate_config():
    """Make sure all key-value pairs within the config are set"""
    missing_values = False
    for section, items in _config.items():
        # Only check for key-value pairs
        if not isinstance(items, dict):
            continue
        unset = [key for key, item in items.items() if not item]
        for key in unset:
            missing_values = True
            print(f'{section}.{key} is not set within the config!')
    if missing_values:
        exit('Missing values detected!')
validate_config()

# Get values from the database section
_get = lambda entry: get('database', entry)
DB_HOST = _get('host')
DB_DATABASE = _get('database')
DB_USER = _get('user')
DB_PASSWORD = _get('pasword')

# Get values from the database-tables section
_get = lambda entry: get('database-tables', entry)
BLOCKS_TABLE = _get('coreprotect_blocks')
USERS_TABLE = _get('coreprotect_users')
WORLDS_TABLE = _get('coreprotect_worlds')
POSITIONS_TABLE = _get('whimc_positions')
OBSERVATIONS_TABLE = _get('whimc_observations')

# Get values from the imgur section
_get = lambda entry: get('imgur', entry)
IMGUR_CLIENT_ID = _get('client_id')
IMGUR_CLIENT_SECRET = _get('client_secret')
IMGUR_ALBUM_ID = _get('album_id')

# Load all the worlds
WORLDS = List[World]
for world_object in _config.get('worlds'):
    world = World(**world_object)
    if not os.path.exists(world.image_path):
        print(f'{world.image_path} does not exist!')
        exit()
    WORLDS.append(world)
