from virtual_object import *
from enums import VirtualObjectTypes

class Actuator(VirtualObject):

    def __init__(self, actuator_type):

        super().__init__(self)

        self.set_object_type(VirtualObjectTypes.ACTUATOR)

        self.set_sub_type(actuator_type)
