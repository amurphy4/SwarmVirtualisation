from virtual_object import *
from enums import VirtualObjectTypes

class Actuator(VirtualObject):

    def __init__(self, actuator_type, capacity=None, ticks_per_place=None, obj=None):

        VirtualObject.__init__(self)

        self.set_object_type(VirtualObjectTypes.ACTUATOR)

        self.set_sub_type(actuator_type)

        self.__capacity = capacity
        self.__ticks_per_place = ticks_per_place
        self.__obj_to_place = obj

        self.__ticks = 0
        self.__inventory = []

    def get_capacity(self):
        return self.__capacity

    def set_capacity(self, capacity):
        self.__capacity = capacity

    def get_ticks_per_place(self):
        return self.__ticks_per_place

    def set_ticks_per_place(self, ticks_per_place):
        self.__ticks_per_place = ticks_per_place

    def get_ticks(self):
        return self.__ticks

    def increment_ticks(self):
        self.__ticks = self.__ticks + 1

    def reset_ticks(self):
        self.__ticks = 0

    def get_inventory(self):
        return self.__inventory

    def add_to_inventory(self, obj):
        if len(self.__inventory) < self.__capacity:
            self.__inventory.append(obj)
            return True

        return False

    def remove_from_inventory(self, obj):
        return self.__inventory.remove(obj)

    def remove_from_inventory(self, index):
        return self.__inventory.pop(index)

    def get_obj_to_place(self):
        return self.__obj_to_place

    def set_obj_to_place(self, obj):
        self.__obj_to_place = obj

    def copy(self):
        copy = Actuator(self.get_name(), self.get_sub_type(), self.get_capacity(), self.get_ticks_per_place(), self.get_obj_to_place())
        return copy
        
