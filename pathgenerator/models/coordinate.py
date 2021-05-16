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
        return ((self.x - self.world.top_left_coordinate_x) * scale, (self.z - self.world.top_left_coordinate_z) * scale)

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
