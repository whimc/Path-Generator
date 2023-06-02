from dataclasses import dataclass

@dataclass(frozen=True)
class AreaOfInterest:
    label: str
    x: float
    y: float
    z: float
    height: float
    radius: float
    score: float
