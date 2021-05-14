from configparser import RawConfigParser
from dataclasses import asdict
import json
from pathgenerator.models.world import World

PATH = 'config.ini'

def convert_config():
    parser = RawConfigParser()
    parser.optionxform = str
    parser.read(PATH)

    result = dict()

    for section, contents in parser.items():
        if len(contents) == 0:
            continue
        result[section] = dict()
        for key, value in contents.items():
            result[section][key] = str(value)

    worlds = result.pop('world-ids')
    result['worlds'] = []
    for world, id_ in worlds.items():
        result['worlds'].append(asdict(World(world, world, f"maps/{world}.png", int(id_))))

    with open('config.json', 'w') as file:
        json.dump(result, file, indent=4)

    print('config.ini converted to config.json!')


if __name__ == '__main__':
    convert_config()
