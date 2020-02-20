from PIL import Image, ImageDraw, ImageFont
from math import sqrt
import numpy as np
from datetime import date
from collections import Counter

class Coordinate:
    def __init__(self, sql_input):
        self.world = sql_input[0]
        self.x = sql_input[1]
        self.y = sql_input[2]
        self.z = sql_input[3]
        self.data = sql_input[4]

    def scaled_3d_coord(self):
        """Scales the Coordinate to a scaled 3d coordinate
        
        Returns:
            (x, y, z) -- 3-d tuple containing the scaled x, y, z coordiantes
        """
        return (self.x + 512, self.y, self.z + 512)
    
    def scaled_2d_coord(self):
        """Scales the Coordinate to a 2d coordiante (excluding Y)
        
        Returns:
            (x, z) -- 2-d tuple containing the scaled x, z coordinates
        """
        return (self.x + 512, self.z + 512)

def scaleToMap(coord):
    if len(coord) == 2:
        return (coord[0] + 512, coord[1] + 512)
    return (coord[0] + 512, coord[1], coord[2] + 512)


def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]


def line(draw, coord1: Coordinate, coord2: Coordinate):
    """Draws a line between two given Coordinates.
    The color of the line depends on the Y value (low = black, high = white)
    
    Arguments:
        draw {Pillow.ImageDraw} -- The ImageDraw to draw on
        coord1 {Coordinate} -- Coordinate of the original position
        coord2 {Coordinate} -- Coordinate of the next position
    """
    #               R    G    B
    # low    black: 0    0    0
    # high   white: 225  225  255

    # Limit elevation to be between 70 and 120
    ll = 70.0
    ul = 120.0

    pos1 = coord1.scaled_3d_coord()
    pos2 = coord2.scaled_3d_coord()
    elev = max(ll, min(pos1[1], ul))

    r = int(scale(elev, (ll, ul), (0.0, 255.0)))
    g = int(scale(elev, (ll, ul), (0.0, 255.0)))
    b = int(scale(elev, (ll, ul), (0.0, 255.0)))

    draw.line([(pos1[0], pos1[2]), (pos2[0], pos2[2])], (r, g, b), 4)


def dot(draw, coord: Coordinate, color, size=2):
    """Draws a dot at the given map Coordinate with the given color.
    
    Arguments:
        draw {PIL.ImageDraw} -- The ImageDraw to draw on
        coord {Coordinate} -- Where to the place the dot
        color {str} -- Pillow color to make the dot
    
    Keyword Arguments:
        size {int} -- Size of the dot (default: {2})
    """
    pos = coord.scaled_2d_coord()
    x = (pos[0] - size, pos[1] - size)
    z = (pos[0] + size, pos[1] + size)

    draw.ellipse([x, z], fill=color)


def heat_bubble(draw, coord: Coordinate, color):
    """Draws a heat bubble at the given map Coordinate with the given color.
    
    Arguments:
        draw {PIL.ImageDraw} -- The ImageDraw to draw on
        coord {Coordinate} -- Where to place the bubble
        color {str} -- Pillow color for bubble
    """ 

    dot(draw, coord, color, 5)


def drawText(draw, pos, text, color='white', size=20, outline=True):
    """Draws text at the given x, y coodinates on the image
    
    Arguments:
        draw {PIL.ImageDraw} -- The ImageDraw to write on
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
    try:
        font = ImageFont.truetype('arial.ttf', size)
    except:
        font = None
        
    if outline:
        draw.text((x-1, y), text, font=font, fill=shadowColor)
        draw.text((x+1, y), text, font=font, fill=shadowColor)
        draw.text((x, y-1), text, font=font, fill=shadowColor)
        draw.text((x, y+1), text, font=font, fill=shadowColor)

    draw.text(pos, text, color, font=font)


def draw_positions(draw_dict, pos_data):
    """Draws positions onto map images. First position is a green dot,
    last position is a red dot. Elevation changes line colors.
    (low = black, high = white)
    
    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        pos_data {list} -- (world_name, x, y, z, time) data tuple list

    Returns:
        dict -- Dictionary keep track of distance traveled per world
    """
    counts = Counter()

    if not pos_data:
        return counts

    prev_coord = None
    first_pos = True
    for entry in pos_data:
        coord = Coordinate(entry)

        if not prev_coord:
            prev_coord = coord
            continue

        if coord.data - prev_coord.data > 10:
            prev_coord = coord
            continue

        if coord.world not in draw_dict:
            continue
        map_draw = draw_dict[coord.world]

        if coord.world != prev_coord.world:
            # Finish off the previous image path
            dot(draw_dict[prev_coord.world], prev_coord, 'red')

            prev_coord = None
            first_pos = True
            prev_coord = coord
            continue

        cur = coord.scaled_3d_coord()
        prev = prev_coord.scaled_3d_coord()

        dist = np.linalg.norm(np.array(cur) - np.array(prev))
        counts[coord.world] += dist

        line(map_draw, prev_coord, coord)
        if first_pos:
            dot(map_draw, prev_coord, 'green')
            first_pos = False
        prev_coord = coord

    dot(draw_dict[prev_coord.world], prev_coord, 'red')

    return counts

def draw_observations(draw_dict, obs_data):
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
        coord = Coordinate(entry)

        if coord.world not in draw_dict:
            continue
        map_draw = draw_dict[coord.world]

        dot(map_draw, coord, 'red')
        drawText(map_draw, coord.scaled_2d_coord(), coord.data)
        counts[coord.world] += 1
    
    return counts


def draw_blocks(draw_dict, block_data):
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
        coord = Coordinate(entry)
        broken = coord.data

        if coord.world not in draw_dict:
            continue
        map_draw = draw_dict[coord.world]

        color = (0, 255, 0, 100)
        if broken:
            color = (255, 0, 0, 100)
        
        heat_bubble(map_draw, coord, color)
        counts[coord.world] += 1
    
    return counts


def draw_path_image(draw_dict, username, start_time, end_time,
                    pos_data, block_data, obs_data, gen_empty=False):
    """Creates the completed image with all the gathered data.
    
    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        username {str} -- Username of player
        start_time {int} -- Start Unix time
        end_time {int} -- End Unix time
        pos_data {list} -- (world_name, x, y, z, time) data tuple list
        block_data {list} -- (world_name, x, y, z, interact_bool) data tuple list
        obs_data {list} -- (world_name, x, y, z, observation) data tuple list
    
    Keyword Arguments:
        gen_empty {bool} -- Whether to generate empty images or not (default: {False})

    Returns:
        {dict} -- {'world_name': ImageDraw} dictionary after parsing with gen_empty
    """

    # Counts to display per map
    distances = draw_positions(draw_dict, pos_data)
    blocks = draw_blocks(draw_dict, block_data)
    observations = draw_observations(draw_dict, obs_data)
    
    # Duration in minutes
    duration = round((end_time - start_time) / 60, 2)

    # Formatted dates for start / end times
    start_date = date.fromtimestamp(start_time).strftime('%b %d, %Y')
    end_date = date.fromtimestamp(end_time).strftime('%b %d, %Y')

    if not gen_empty:
        # keys = draw_dict.keys().copy()
        # for name in keys:
        #     if not distances[name] and not blocks[name] and not observations[name]:
        #         draw_dict.pop(name)
        draw_dict = { key:val for key, val in draw_dict.items() if 
            distances[key] or blocks[key] or observations[key] }

    for name, draw in draw_dict.items():
        height = 1034
        vSpace = 30
        drawText(draw, (10, height), "Username:", 'black', 25)
        drawText(draw, (10 + 140, height), username, 'red', 25)
        height += vSpace

        drawText(draw, (10, height), "Duration:", 'black', 25)
        drawText(draw, (10 + 110, height), "%s minutes" % duration, 'red', 25)
        height += vSpace

        drawText(draw, (10, height), "Start and end time:", 'black', 25)
        drawText(draw, (10 + 225, height), "%s through %s" %
                (start_date, end_date), 'red', 25)
        height += vSpace

        drawText(draw, (10, height), "Distance Traveled:", 'black', 25)
        drawText(draw, (10 + 220, height), "%s blocks" % int(distances[name]), 'red', 25)
        height += vSpace

        drawText(draw, (10, height), "Blocks Interacted:", 'black', 25)
        drawText(draw, (10 + 210, height), "%s blocks" % blocks[name], 'red', 25)
        height += vSpace

        drawText(draw, (10, height), "Observations made:", 'black', 25)
        drawText(draw, (10 + 235, height), "%s observations" %
                observations[name], 'red', 25)
    
    return draw_dict
