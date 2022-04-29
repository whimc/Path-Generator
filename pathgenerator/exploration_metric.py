from argparse import ArgumentParser, FileType
import numpy as np
import csv

from pathgenerator.models.coordinate import Coordinate
from pathgenerator.config import ALL_WORLDS, WORLDS
from pathgenerator.utils.data_fetcher import DataFetcher
from pathgenerator.utils import scale


def get_metrics(data):
    map_matrices = {world.display_name:np.zeros((10, 10)) for world in ALL_WORLDS}

    for entry in data:
        coord = Coordinate(*entry)

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

    return {world:int(np.sum(metrics)) for world, metrics in map_matrices.items()}

def write_metrics(output_file, user_metrics):
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(['username'] + [world.display_name for world in ALL_WORLDS])
    for user, metrics in user_metrics.items():
        csv_writer.writerow([user] + [metrics[world.display_name] for world in ALL_WORLDS])

if __name__ == '__main__':
    def csv_file(s):
        file = FileType('w')(s)
        return open(file.name, 'w', newline='')

    parser = ArgumentParser(prog='pathgenerator.exploration_metric')
    parser.add_argument('position_output', type=csv_file, help='Output for exploration metrics')
    parser.add_argument('observation_output', type=csv_file, help='Output for observation metrics')
    parser.add_argument('start_time', type=int, help='Unix start time')
    parser.add_argument('end_time', type=int, help='Unix end time')
    parser.add_argument('username', nargs='+', help='Username of the player')

    options = vars(parser.parse_args())

    start_time = options.get('start_time')
    end_time = options.get('end_time')
    usernames = options.get('username')

    # Fetch all data for the given users
    user_data = dict()
    for username in usernames:
        print(f"Fetching data for {username}")
        user_data[username] = DataFetcher(username, start_time, end_time)

    # Generate the exploration metrics
    exploration_metrics = dict()
    for username in usernames:
        data = user_data.get(username)
        exploration_metrics[username] = get_metrics(data.position_data)

    # Generate the observation metrics
    observation_metrics = dict()
    for username in usernames:
        data = user_data.get(username)
        observation_metrics[username] = get_metrics(data.observation_data)

    # Generate the CSV files for the metrics
    write_metrics(options.get('position_output'), exploration_metrics)
    write_metrics(options.get('observation_output'), observation_metrics)
