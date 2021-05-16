from argparse import ArgumentParser, FileType
import numpy as np
from PIL import Image
import csv

from pathgenerator.models.coordinate import Coordinate
from pathgenerator.config import ALL_WORLDS, WORLDS
from pathgenerator.utils.data_fetcher import DataFetcher
from pathgenerator.map_drawer import scale


def get_exploration_metrics(position_data):
    map_matrices = {world.display_name:np.zeros((10, 10)) for world in ALL_WORLDS}

    for pos in position_data:
        coord = Coordinate(*pos)

        for world in WORLDS[coord.world_name]:
            coord.world = world
            min_x = world.top_left_coordinate_x
            min_z = world.top_left_coordinate_z
            max_x = min_x + world.img_obj.width / world.pixel_to_block_ratio
            max_z = min_z + world.img_obj.height / world.pixel_to_block_ratio
            if not coord.is_inside_view:
                continue

            row = int(scale(coord.x, (min_x, max_x), (0, 10)))
            col = int(scale(coord.z, (min_z, max_z), (0, 10)))

            map_matrices[world.display_name][row][col] = 1

    return map_matrices

if __name__ == '__main__':
    parser = ArgumentParser(prog='pathgenerator.exploration_metric')
    parser.add_argument('output', type=FileType('w'), help='Output file name')
    parser.add_argument('start_time', type=int, help='Unix start time')
    parser.add_argument('end_time', type=int, help='Unix end time')
    parser.add_argument('username', nargs='+', help='Username of the player')

    options = vars(parser.parse_args())

    start_time = options.get('start_time')
    end_time = options.get('end_time')
    usernames = options.get('username')

    # Load all the world images
    for world in ALL_WORLDS:
        world.img_obj = Image.open(world.image_path)

    metrics = dict()
    for username in usernames:
        print(f"Fetching data for {username}")
        fetcher = DataFetcher(username, start_time, end_time)
        metrics[username] = get_exploration_metrics(fetcher.position_data)

    output = options.get('output')
    csv_writer = csv.writer(output)
    csv_writer.writerow(['username'] + [world.display_name for world in ALL_WORLDS])

    # Write all users to the csv
    for user, metrics in metrics.items():
        csv_writer.writerow([user] + [np.sum(metrics[world.display_name]) for world in ALL_WORLDS])
