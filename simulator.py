import cv2, numpy, threading, math

from enums import *

class Simulator():

    __instance = None

    @staticmethod
    def getInstance():
        if Simulator.__instance == None:
            Simulator()

        return Simulator.__instance

    def __init__(self):
        if Simulator.__instance != None:
            raise Exception("Invalid invocation of singleton class")
        else:
            Simulator.__instance = self
        
        self.__bots = None
        self.__environment = None
        self.__frame = None

        self.__callback = None
        self.__data_method = None

        self.__looping = True

    def start(self):
        thread = SimulationThread(2, "simulation", 2)
        thread.start()

    def stop(self):
        self.__looping = False

    def set_callback(self, callback):
        self.__callback = callback

    def set_data_method(self, method):
        self.__data_method = method

    def get_data(self):
        self.__bots, self.__environment, self.__frame = self.__data_method()

    def circle_sensor(self, bot, sensor):
        height = self.__frame.shape[0]
        width = self.__frame.shape[1]

        # Create blank mask
        img = numpy.zeros((height, width), numpy.uint8)

        # TODO: Fix this to work with multiple environment objects
        for env in self.__environment:
            # Add circle for environment object
            cv2.circle(img, self.__environment[0].get_position(), self.__environment[0].get_radius(), 255)

            # Identify circle using mask - This needs fixin' tho
            points = numpy.transpose(numpy.where(img == 255))
        
        in_range = False
        for point in points:
            a = numpy.array((point[1], point[0]))
            b = numpy.array((bot.get_centre().x, bot.get_centre().y))
            euclid = numpy.linalg.norm(a - b)

            if (euclid <= sensor.get_radius()):
                in_range = True
                break;

        if in_range:
            return True

        return False

    def cone_sensor(self, bot, sensor):
        pass

    def line_sensor(self, bot, sensor):
        pass

    def _simulate(self):
        while self.__looping:
            #SIMULATE SHIT

            self.get_data()

            sensor_data = {"bots" : []}

            for bot in self.__bots:                
                data = {"id" : bot.get_id(), "sensors" : []}
                # Simulate sensors for each bot
                for sensor in bot.get_sensors():
                    # Simulate sensor
                    if sensor.get_sub_type() == SensorTypes.CIRCLE:
                        # Simulate fully circular sensor around bot
                        try:
                            in_range = self.circle_sensor(bot, sensor);
                        except AttributeError:
                            break;

                        #print(in_range)

                        if in_range:
                            # Sensor detected something, log this to be returned at the end of the tick
                            data["sensors"].append({sensor.get_name() : True})
                    elif sensor.get_sub_type() == SensorTypes.CONE:
                        pass
                    elif sensor.get_sub_type() == SensorTypes.LINE:
                        pass

                sensor_data["bots"].append(data)

            self.__callback(sensor_data)
                

class SimulationThread(threading.Thread):

    def __init__(self, threadId, name, counter):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.counter = counter


    def run(self):
        Simulator.getInstance()._simulate()
