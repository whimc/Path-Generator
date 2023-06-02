from dataclasses import dataclass, field
from typing import List

from PIL import Image, ImageDraw

from pathgenerator.models.area_of_interest import AreaOfInterest

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
    areas_of_interest: List[AreaOfInterest] = field(default_factory=list)
