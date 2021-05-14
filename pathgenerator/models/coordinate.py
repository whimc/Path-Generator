from dataclasses import dataclass
import typing

@dataclass
class Coordinate:
    """
    Represents a coordinate within a Minecraft map.
    The 'data' attribute is used to hold any kind of data that is tied with the coordinate.
    """

    world: str
    x: float
    y: float
    z: float
    data: typing.Any

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
