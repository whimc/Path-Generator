from dataclasses import dataclass

@dataclass(frozen=True)
class PointOfInterest:
    label: str
    x: float
    y: float
    z: float
    height: float
    radius: float
    value: float
