class VirtualObject():

    def __init__(self, name):

        self.__name = name
        
        self.__object_type = None
        self.__sub_type = None

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name == name

    def get_object_type(self):
        return self.__object_type

    def set_object_type(self, object_type):
        self.__object_type = object_type

    def get_sub_type(self):
        return self.__sub_type

    def set_sub_type(self, sub_type):
        self.__sub_type = sub_type
