from virtual_object import *
from enums.virtual_object import *

class Sensor(VirtualObject):

    def __init__(self, name, sensor_type, _range=None, radius=None, angle_offset=None, tangent=None):

        super().__init__(self, name)

        self.set_object_type(VirtualObjectTypes.SENSOR)

        self.set_sub_type(sensor_type)

        # All posible variable types - some will remain None
        self.__range = _range
        self.__radius = radius
        self.__angle_offset = angle_offset
        self.__tangent = tangent
