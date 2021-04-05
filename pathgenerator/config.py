from configparser import RawConfigParser
from dataclasses import dataclass
import os

PATH = 'config.ini'

_parser = RawConfigParser()
_parser.optionxform = str
_parser.read(PATH)

def validate_config():
    missing_keys = False
    for section, items in _parser.items():
        unset = [key for key, item in items.items() if not item]
        for key in unset:
            missing_keys = True
            print(f'{section}.{key} is not set within the config!')
    if missing_keys:
        exit()
validate_config()

TABLES_SECTION = 'database-tables'
_get = lambda entry: _parser.get(TABLES_SECTION, entry)
BLOCKS_TABLE = _get('coreprotect_blocks')
USERS_TABLE = _get('coreprotect_users')
WORLDS_TABLE = _get('coreprotect_worlds')
POSITIONS_TABLE = _get('whimc_positions')
OBSERVATIONS_TABLE = _get('whimc_observations')

IMGUR_SECTION = 'imgur'
_get = lambda entry: _parser.get(IMGUR_SECTION, entry)
IMGUR_CLIENT_ID = _get('client_id')
IMGUR_CLIENT_SECRET = _get('client_secret')
IMGUR_ALBUM_ID = _get('album_id')

@dataclass
class WorldMeta:
    name: str
    id: int
    img_path: str


WORLDS = []
for world, id_ in _parser['world-ids'].items():
    path = os.path.join('maps', f'{world}.png')
    if not os.path.exists(path):
        print(f'{path} does not exist!')
        exit()
    WORLDS.append(WorldMeta(world, id_, path))

def get(section, key, fallback=None):
    return _parser.get(section, key, fallback=fallback)

def get_dict(section, *keys):
    return { key : get(section, key) for key in keys }

def set(section, key, value):
    set_multi(section, (key, value))

def set_multi(section, *items):
    for key, value in items:
        _parser.set(section, key, value)
    with open(PATH, 'w') as file:
        _parser.write(file)
