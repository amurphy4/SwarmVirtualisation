from virtual_object import *
from enums import VirtualObjectTypes

class Actuator(VirtualObject):

    def __init__(self, actuator_type, capacity=None):

        super().__init__(self)

        self.set_object_type(VirtualObjectTypes.ACTUATOR)

        self.set_sub_type(actuator_type)

        self.__capacity = capacity

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, capacity):
        self.__capacity = capacity
