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
        
        img = numpy.zeros((height, width), numpy.uint8)

        for env in self.__environment:
            cv2.circle(img, self.__environment[0].get_position(), self.__environment[0].get_radius(), 255)
            points = numpy.transpose(numpy.where(img == 255))
            #print(env.get_position())
        
        in_range = False
        for point in points:
            a = numpy.array((point[0], point[1]))
            b = numpy.array((bot.get_centre().x, bot.get_centre().y))
            euclid = numpy.linalg.norm(a - b)
            d = math.sqrt(euclid)
            print(d)
            print("Euclidean: {0}".format(numpy.linalg.norm(numpy.array((point[0], point[1], 0)) - numpy.array((bot.get_centre().x, bot.get_centre().y, 0)))))
            print("({0}, {1}) - ({2}, {3}))".format(point[0], point[1], bot.get_centre().x, bot.get_centre().y))
            if (d <= sensor.get_radius()):
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

                        print(in_range)

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
