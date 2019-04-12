from virtual_object import *
from enums import *

class Sensor(VirtualObject):

    def __init__(self, name, sensor_type, _range=None, radius=None, angle_offset=None, tangent=None):

        VirtualObject.__init__(self, name)

        self.set_object_type(VirtualObjectTypes.SENSOR)

        self.set_sub_type(sensor_type)

        # All posible variable types - some will remain None
        self.__range = _range
        self.__radius = radius
        self.__angle_offset = angle_offset
        self.__tangent = tangent

        self.__is_visible = True

    def get_range(self):
        return self.__range

    def set_range(self, _range):
        self.__range = _range
    
    def get_radius(self):
        return self.__radius

    def set_radius(self, radius):
        self.__radius = radius

    def get_angle_offset(self):
        return self.__angle_offset

    def set_angle_offset(self, angle_offset):
        self.__angle_offset = angle_offset

    def get_tangent(self):
        return self.__tangent

    def set_tangent(self, tangent):
        self.__tangent = tangent

    def get_is_visible(self):
        return self.__is_visible

    def set_is_visible(self, is_visible):
        self.__is_visible = is_visible

    def copy(self):
        copy = Sensor(self.get_name(), self.get_sub_type(), self.get_range(), self.get_radius(), self.get_angle_offset(), self.get_tangent())
        return copy
