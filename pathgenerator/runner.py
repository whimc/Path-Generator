import os
from pathgenerator.utils.data_fetcher import DataFetcher
from threading import Thread

import pathgenerator.utils.map_drawer as map_drawer
import pathgenerator.utils.imgur_uploader as imgur_uploader

OUTPUT_DIR = 'output'

def generate_images(username, start_time: int, end_time: int, gen_empty=False):
    """Generate path images for all worlds for the given user between `start_time` and `end_time`.
    Saves path images within `output/`.

    Arguments:
        username {str} -- Username of target player
        start_time {int} -- Unix start time
        end_time {int} -- Unix end time
    """
    fetcher = DataFetcher(username, start_time, end_time)

    pos_data = fetcher.position_data
    block_data = fetcher.block_data
    obs_data = fetcher.observation_data

    print('\nGathering data:')
    print(f'\t{len(pos_data)} total positions')
    print(f'\t{len(block_data)} total blocks')
    print(f'\t{len(obs_data)} total observations')
    print('')

    drawn_worlds = map_drawer.draw_path_image(username, start_time, end_time,
                                pos_data, block_data, obs_data, gen_empty)

    user_output = os.path.join(OUTPUT_DIR, username, f"{start_time}-{end_time}")
    if not os.path.exists(user_output):
        os.makedirs(user_output)

    # If no maps were generated, do nothing
    if not drawn_worlds:
        return

    print('\nSaving images:')
    threads = []
    for world in drawn_worlds:
        name = world.display_name
        img = world.img_obj

        gen_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        spec_path = os.path.join(user_output, f"{name}.png")

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

    if os.path.exists(OUTPUT_DIR):
        for file_name in os.listdir(OUTPUT_DIR):
            path = os.path.join(OUTPUT_DIR, file_name)
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
    for file_name in os.listdir(OUTPUT_DIR):
        path = os.path.join(OUTPUT_DIR, file_name)
        if not os.path.isfile(path):
            continue
        img_name = f'{username}-{start_time}-{end_time}_{file_name}'
        path_name_dict[path] = img_name

    if not path_name_dict:
        print('There are no images to upload!')
        return None

    print('Uploading images to Imgur...')

    return imgur_uploader.upload_to_imgur(path_name_dict, overwrite)
