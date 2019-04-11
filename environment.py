from virtual_object import *
from enums import *

class Environment(VirtualObject):

    def __init__(self, name, environment_type, position=None, radius=None):

        VirtualObject.__init__(self, name)

        self.set_object_type(VirtualObjectTypes.ENVIRONMENT)

        self.set_sub_type(environment_type)

        self.__position = position
        self.__radius = radius

    def get_position(self):
        return self.__position

    def set_position(self, position):
        self.__position = position

    def get_radius(self):
        return self.__radius

    def set_radius(self, radius):
        self.__radius = radius
