from dataclasses import dataclass
from PIL import Image, ImageDraw

@dataclass
class World:
    display_name: str
    world_name: str
    image_path: str
    coreprotect_id: int
    pixel_to_block_ratio: float = 1.0
    top_left_coordinate_x: int = -512
    top_left_coordinate_z: int = -512
    draw_obj: ImageDraw.Draw = None
    img_obj: Image = None
