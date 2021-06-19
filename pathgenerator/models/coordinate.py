from dataclasses import dataclass
import typing

from pathgenerator.models.world import World

@dataclass
class Coordinate:
    """
    Represents a coordinate within a Minecraft map.
    The 'data' attribute is used to hold any kind of data that is tied with the coordinate.
    """

    world_name: str
    x: float
    y: float
    z: float
    data: typing.Any
    world: World = None

    @property
    def coord_2d(self):
        """
        Scales the Coordinate to a 2d coordinate (excluding Y).
        MUST have the 'world' attribute set!

        Returns:
            (x, z) -- 2-d tuple containing the scaled x, z coordinates
        """
        scale = self.world.pixel_to_block_ratio
        x = (self.x - self.world.top_left_coordinate_x) * scale
        z = (self.z - self.world.top_left_coordinate_z) * scale
        return (x, z)

    @property
    def coord_2d_unscaled(self):
        """Get a tuple of the unscaled 2d coordinates"""
        return (self.x, self.z)

    @property
    def coord_3d(self):
        """
        Scales the Coordinate to a scaled 3d coordinate
        MUST have the 'world' attribute set!

        Returns:
            (x, y, z) -- 3-d tuple containing the scaled x, y, z coordiantes
        """
        x, z = self.coord_2d
        return (x, self.y, z)

    @property
    def coord_3d_unscaled(self):
        """Get a tuple of the unscaled 3d coordinates"""
        return (self.x, self.y, self.z)

    @property
    def is_inside_view(self):
        """Determines if this coordinate is inside of the World's view"""
        min_x = self.world.top_left_coordinate_x
        min_z = self.world.top_left_coordinate_z
        max_x = min_x + self.world.img_obj.width / self.world.pixel_to_block_ratio
        max_z = min_z + self.world.img_obj.height / self.world.pixel_to_block_ratio
        return min_x < self.x < max_x and min_z < self.z < max_z
