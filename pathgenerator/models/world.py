from dataclasses import dataclass

@dataclass
class World:
    display_name: str
    world_name: str
    image_path: str
    coreprotect_id: int
    pixel_to_block_ratio: int = 1
    top_left_coordinate_x: int = -512
    top_left_coordinate_z: int = -512
