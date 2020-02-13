from PIL import Image, ImageDraw, ImageFont
from math import sqrt
import numpy as np

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
    font = ImageFont.truetype('arial.ttf', size)

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
        pos_data {list} -- (world_name, x, y, z, time) data tuple
    """
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

        line(map_draw, prev_coord, coord)
        if first_pos:
            dot(map_draw, prev_coord, 'green')
            first_pos = False
        prev_coord = coord


    dot(draw_dict[prev_coord.world], prev_coord, 'red')

def draw_observations(draw_dict, obs_data):
    """Draws observations onto map images
    
    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        obs_data {list} -- (world_name, x, y, z, observation) data tuple
    """
    for entry in obs_data:
        coord = Coordinate(entry)

        if coord.world not in draw_dict:
            continue
        map_draw = draw_dict[coord.world]

        dot(map_draw, coord, 'red')
        drawText(map_draw, coord.scaled_2d_coord(), coord.data)


def draw_blocks(draw_dict, block_data):
    """Draws blocks onto map images
    
    Arguments:
        draw_dict {dict} -- {'world_name': ImageDraw} dictionary
        block_data {list} -- (world_name, x, y, z, interact_bool) data tuple
    """
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


# TODO: Rewrite
def createImage(img, sessions, worldName, worldId):
    """
    Creates a new img from the given map image and sessions
    Returns None if there were no interactions in the given sessions on the map
    """

    footer = Image.new('RGB', (img.width, img.height + 200),
                       color=(230, 230, 230))
    footer.paste(img)

    draw = ImageDraw.Draw(footer, "RGBA")

    hasData = False
    duration = 0
    distance = 0
    blocks = 0
    observations = 0

    for currSession in sessions:
        currHasData = False

        temp = drawBlockData(draw, currSession, worldId)
        if temp:
            currHasData = True
            blocks += temp

        temp = drawPositions(draw, currSession, worldName)
        if temp:
            currHasData = True
            distance += temp

        temp = drawObservations(draw, currSession, worldName)
        if temp:
            currHasData = True
            observations += temp

        if currHasData:
            duration += currSession.end_time - currSession.start_time
            hasData = True

    if not hasData:
        return None

    # Rounding the duration to hours and the distance to an integer
    duration = round(duration / (60.0*60.0), 2)
    distance = int(distance)

    # Getting a formatted version of the start and end times
    startDate = datetime.fromtimestamp(
        sessions[0].start_time).strftime('%b %d, %Y')
    endDate = datetime.fromtimestamp(
        sessions[-1].end_time).strftime('%b %d, %Y')

    # Really ugly hard coded text for statistics
    height = 1034
    vSpace = 30
    drawText(draw, (10, height), "Username:", 'black', 25)
    drawText(draw, (10 + 140, height), sessions[0].username, 'red', 25)
    height += vSpace

    drawText(draw, (10, height), "Duration:", 'black', 25)
    drawText(draw, (10 + 110, height), "%s hours" % duration, 'red', 25)
    height += vSpace

    drawText(draw, (10, height), "Start and end time:", 'black', 25)
    drawText(draw, (10 + 225, height), "%s through %s" %
             (startDate, endDate), 'red', 25)
    height += vSpace

    drawText(draw, (10, height), "Distance Traveled:", 'black', 25)
    drawText(draw, (10 + 220, height), "%s blocks" % distance, 'red', 25)
    height += vSpace

    drawText(draw, (10, height), "Blocks Interacted:", 'black', 25)
    drawText(draw, (10 + 210, height), "%s blocks" % blocks, 'red', 25)
    height += vSpace

    drawText(draw, (10, height), "Observations made:", 'black', 25)
    drawText(draw, (10 + 235, height), "%s observations" %
             observations, 'red', 25)
    height += vSpace

    return footer
