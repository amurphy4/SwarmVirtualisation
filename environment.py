from virtual_object import *
from enums import *

class Environment(VirtualObject):

    def __init__(self, name, environment_type, position=None, radius=None, capacity=None):

        VirtualObject.__init__(self, name)

        self.set_object_type(VirtualObjectTypes.ENVIRONMENT)

        self.set_sub_type(environment_type)

        self.__position = position
        self.__radius = radius
        self.__capacity = capacity
        self.__is_visible = False

    def get_position(self):
        return self.__position

    def set_position(self, position):
        self.__position = position

    def get_radius(self):
        return self.__radius

    def set_radius(self, radius):
        self.__radius = radius

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, capacity):
        self.__capacity = capacity

    def get_is_visible(self):
        return self.__is_visible

    def set_is_visible(self, is_visible):
        self.__is_visible = is_visible

    def copy(self):
        copy = Environment(self.get_name(), self.get_sub_type(), self.get_position(), self.get_radius())
        return copy
