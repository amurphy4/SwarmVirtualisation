from enum import Enum

class SensorTypes(Enum):

    # Current sensor types available
    CONE = "Cone with radius, tangent and angle offset variables from centre of bot, sensing within cone"
    CIRCLE = "Circle with radius R from centre of bot, sensing in all directions"
    LINE = "Direct line in front of a point with distance and angle offset variables e.g. laser"
