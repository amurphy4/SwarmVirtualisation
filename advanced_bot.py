from SwarmTracking.objects import Bot as B

class Bot(B):

    def __init__(self, bot):
        # Get bot values for calling super init
        tl, tr, br, bl = bot.get_corners()
        bot_id = bot.get_id()
        
        B.__init__(self, tl, tr, br, bl, bot_id)

        self.__sensors = []
        self.__actuators = []

        self.__ip = None

    def get_sensors(self):
        return self.__sensors

    def add_sensor(self, sensor):
        return self.__sensors.append(sensor)

    def remove_sensor(self, sensor):
        return self.__sensors.remove(sensor)

    def get_actuators(self):
        return self.__actuators

    def add_actuator(self, actuator):
        return self.append(actuator)

    def remove_actuator(self, actuator):
        return self.remove(actuator)

    def get_ip(self):
        return self.__ip

    def set_ip(self, ip):
        self.__ip = ip
