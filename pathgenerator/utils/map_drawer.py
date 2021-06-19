from PIL import ImageFont, Image, ImageDraw as ID
from PIL.ImageDraw import ImageDraw
import numpy as np
from datetime import date
from collections import Counter
import os

from pathgenerator.models.coordinate import Coordinate
from pathgenerator.exploration_metric import get_metrics
from pathgenerator.config import ALL_WORLDS, WORLDS, reload_world_images
from pathgenerator.utils import scale, resized_copy


def line(draw: ImageDraw, coord1: Coordinate, coord2: Coordinate):
    """Draws a line between two given Coordinates.
    The color of the line depends on the Y value (low = black, high = white)

    Arguments:
        draw {ImageDraw} -- The ImageDraw to draw on
        coord1 {Coordinate} -- Coordinate of the original position
        coord2 {Coordinate} -- Coordinate of the next position
    """
    #               R    G    B
    # low    black: 0    0    0
    # high   white: 225  225  255

    # Limit elevation to be between 70 and 120
    ll = 70.0
    ul = 120.0

    pos1 = coord1.coord_3d
    pos2 = coord2.coord_3d
    elev = max(ll, min(pos1[1], ul))

    # The RGB tuple to make the gray for the given elevation
    gray = (int(scale(elev, (ll, ul), (0.0, 255.0))), ) * 3

    draw.line([(pos1[0], pos1[2]), (pos2[0], pos2[2])], gray, 4)

def dot(draw: ImageDraw, coord: Coordinate, color: str, size: int = 2):
    """Draws a dot at the given map Coordinate with the given color.

    Arguments:
        draw {ImageDraw} -- The ImageDraw to draw on
        coord {Coordinate} -- Where to the place the dot
        color {str} -- Pillow color to make the dot

    Keyword Arguments:
        size {int} -- Size of the dot (default: {2})
    """
    pos = coord.coord_2d
    x = (pos[0] - size, pos[1] - size)
    z = (pos[0] + size, pos[1] + size)

    draw.ellipse([x, z], fill=color)

def heat_bubble(draw: ImageDraw, coord: Coordinate, color: str):
    """Draws a heat bubble at the given map Coordinate with the given color.

    Arguments:
        draw {ImageDraw} -- The ImageDraw to draw on
        coord {Coordinate} -- Where to place the bubble
        color {str} -- Pillow color for bubble
    """

    dot(draw, coord, color, 5)


def drawText(draw: ImageDraw, pos: tuple, text: str, color: str = 'white', size: int = 20, outline: bool = True):
    """Draws text at the given x, y coodinates on the image

    Arguments:
        draw {ImageDraw} -- The ImageDraw to write on
        pos {tuple} -- (x, z) coordinate for the text
        text {str} -- Text to write

    Keyword Arguments:
        color {str} -- Pillow color for the text (default: {'white'})
        size {int} -- Size of the text (default: {20})
        outline {bool} -- Whether to outline the text (default: {True})
    """

    x = pos[0]
    y = pos[1]

    shadowColor = 'black'
    font = ImageFont.truetype(os.path.join('.', 'arial.ttf'), size)

    if outline:
        draw.text((x-1, y), text, font=font, fill=shadowColor)
        draw.text((x+1, y), text, font=font, fill=shadowColor)
        draw.text((x, y-1), text, font=font, fill=shadowColor)
        draw.text((x, y+1), text, font=font, fill=shadowColor)

    draw.text(pos, text, color, font=font)


def draw_positions(pos_data):
    """Draws positions onto map images. First position is a green dot,
    last position is a red dot. Elevation changes line colors.
    (low = black, high = white)

    Arguments:
        pos_data {list} -- (world_name, x, y, z, time) data tuple list

    Returns:
        dict -- Dictionary keeping track of distance traveled per world
    """
    counts = Counter()

    if not pos_data:
        return counts

    prev_coord = None
    first_pos = True
    for entry in pos_data:
        coord = Coordinate(*entry)

        if not prev_coord:
            prev_coord = coord
            continue

        # The coordinate's "data" is the time of the location
        # Don't draw a line if the two positions happend more than 10 seconds apart
        if coord.data - prev_coord.data > 10:
            prev_coord = coord
            continue

        different_world = coord.world_name != prev_coord.world_name

        for world in WORLDS[coord.world_name]:
            coord.world = world
            prev_coord.world = world

            # If we switched maps, finish the path by drawing a red dot at the stopping position
            if different_world:
                # Finish off the previous image path
                dot(prev_coord.world.draw_obj, prev_coord, 'red')
                continue

            dist = np.linalg.norm(np.array(coord.coord_3d) - np.array(prev_coord.coord_3d))
            counts[world.display_name] += dist

            map_draw = world.draw_obj
            line(map_draw, prev_coord, coord)

            # Draw a green dot at the initial position
            if first_pos:
                dot(map_draw, prev_coord, 'green')

        if first_pos:
            first_pos = False

        if different_world:
            prev_coord = None
            first_pos = True

        prev_coord = coord

    # Finish off the last map
    dot(prev_coord.world.draw_obj, prev_coord, 'red')

    return counts

def draw_observations(obs_data):
    """Draws observations onto map images

    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        obs_data {list} -- (world_name, x, y, z, observation) data tuple list

    Returns:
        dict -- Dictionary keeping track of observations per world
    """
    counts = Counter()

    if not obs_data:
        return counts

    for entry in obs_data:
        coord = Coordinate(*entry)

        for world in WORLDS[coord.world_name]:
            coord.world = world

            map_draw = world.draw_obj
            dot(map_draw, coord, 'red')

            # The coordinate's "data" is the text of the observation
            drawText(map_draw, coord.coord_2d, str(coord.data))
            counts[world.display_name] += 1

    return counts


def draw_blocks(block_data):
    """Draws blocks onto map images

    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        block_data {list} -- (world_name, x, y, z, interact_bool) data tuple list

    Returns:
        dict -- Dictionary keeping tracking of blocks interacted with per world
    """
    counts = Counter()

    if not block_data:
        return counts

    for entry in block_data:
        coord = Coordinate(*entry)

        # The coordinate's "data" is a boolean whether or not the block was broken
        broken = coord.data

        color = (0, 255, 0, 100)
        if broken:
            color = (255, 0, 0, 100)

        for world in WORLDS[coord.world_name]:
            coord.world = world
            heat_bubble(world.draw_obj, coord, color)
            counts[world.display_name] += 1

    return counts


def draw_path_image(username, start_time, end_time,
                    pos_data, block_data, obs_data, gen_empty=False):
    """Creates the completed image with all the gathered data.

    Arguments:
        username {str} -- Username of player
        start_time {int} -- Start Unix time
        end_time {int} -- End Unix time
        pos_data {list} -- (world_name, x, y, z, time) data tuple list
        block_data {list} -- (world_name, x, y, z, interact_bool) data tuple list
        obs_data {list} -- (world_name, x, y, z, observation) data tuple list

    Keyword Arguments:
        gen_empty {bool} -- Whether to generate empty images or not (default: {False})

    Returns:
        {list} -- List of 'World's that were drawn
    """
    reload_world_images()

    # Counts to display per map
    distances = draw_positions(pos_data)
    blocks = draw_blocks(block_data)
    observations = draw_observations(obs_data)

    exploration_metrics = get_metrics(pos_data)
    observation_metrics = get_metrics(obs_data)

    # Duration in minutes
    duration = round((end_time - start_time) / 60, 2)

    # Formatted dates for start / end times
    start_date = date.fromtimestamp(start_time).strftime('%b %d, %Y')
    end_date = date.fromtimestamp(end_time).strftime('%b %d, %Y')

    drawn_worlds = []

    for world in ALL_WORLDS:
        name = world.display_name

        # Skip generating empty maps
        if not gen_empty and distances[name] == 0:
            continue

        # Resize the image to have a width of 1024 and add space for the footer
        footer_height = 215
        resized = resized_copy(world.img_obj, 1024)
        with_footer = Image.new('RGB', (resized.width, resized.height + footer_height), color=(230, 230, 230))
        with_footer.paste(resized)

        world.img_obj = with_footer
        draw = world.draw_obj = ID.Draw(with_footer)
        draw = world.draw_obj

        height = world.img_obj.height - footer_height
        vertical_space = 30

        text = lambda width, text, color: drawText(draw, (10 + width, height), text, color, 25)

        text(0, 'Username:', 'black')
        text(140, username, 'red')
        height += vertical_space

        text(0, 'Duration:', 'black')
        text(110, f"{duration} minutes", 'red')
        height += vertical_space

        text(0, 'Start and End Time:', 'black')
        text(230, f"{start_date} through {end_date}", 'red')
        height += vertical_space

        text(0, 'Distance Traveled:', 'black')
        text(220, f"{int(distances[name])} blocks", 'red')
        height += vertical_space

        text(0, 'Blocks Interacted:', 'black')
        text(210, f"{blocks[name]} blocks", 'red')
        height += vertical_space

        text(0, 'Observations Made:', 'black')
        text(235, f"{observations[name]} observations", 'red')
        height += vertical_space

        text(0, 'Exploration Metric:', 'black')
        text(220, str(exploration_metrics[name]), 'red')
        text(280, 'Observation Metric:', 'black')
        text(510, str(observation_metrics[name]), 'red')

        drawn_worlds.append(world)

    return drawn_worlds
