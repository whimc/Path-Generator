from configparser import RawConfigParser

_parser = RawConfigParser()
_parser.optionxform = str
_parser.read('config.ini')

_get = lambda entry: _parser.get('database-tables', entry)

BLOCKS_TABLE = _get('coreprotect_blocks')
USERS_TABLE = _get('coreprotect_users')
WORLDS_TABLE = _get('coreprotect_worlds')
POSITIONS_TABLE = _get('whimc_positions')
OBSERVATIONS_TABLE = _get('whimc_observations')

WORLD_IDS = _parser['world-ids']
