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

        env_points = []

        # Identify points for all environment objects 
        for env in self.__environment:
            # Add circle for environment object
            cv2.circle(img, env.get_position(), env.get_radius(), 255)

            # Identify circle using mask
            points = numpy.transpose(numpy.where(img == 255))
            env_points.append(points)

        for points in env_points:
            for point in points:
                a = numpy.array((point[1], point[0]))
                b = numpy.array((bot.get_centre().x, bot.get_centre().y))
                euclid = numpy.linalg.norm(a - b)

                if (euclid <= sensor.get_radius()):
                    # In range!
                    return True

        # Not in range
        return False

    def cone_sensor(self, bot, sensor):
        height = self.__frame.shape[0]
        width = self.__frame.shape[1]

        # Create blank mask
        img = numpy.zeros((height, width), numpy.uint8)

        # Get positions from bot to calculate tag offset
        front = bot.get_front_point()
        centre = bot.get_centre()

        # Calculate tag offset with respect to Y axis
        a = numpy.array((front.x, front.y))
        b = numpy.array((centre.x, centre.y))
        dist = numpy.linalg.norm(a - b)

        pointY = centre.y + dist

        # Calculate angle between top of tag and Y axis
        result = math.atan2(pointY - centre.y, centre.x - centre.x) + math.atan2(front.y - centre.y, front.x - centre.x)
        angle = math.degrees(result)

        # Calculate start and end angles for cone sensor
        start_angle = angle - int(sensor.get_cone_angle() / 2) + sensor.get_angle_offset()
        end_angle = start_angle + sensor.get_cone_angle()

        # Add sensor to image
        radius = sensor.get_radius()
        cv2.ellipse(img, (centre.x, centre.y), (radius, radius), 0, start_angle, end_angle, 255)

        # Get all points in sensor range
        sensor_points = numpy.transpose(numpy.where(img == 255))

        # Re-create blank mask
        img = numpy.zeros((height, width), numpy.uint8)

        env_points = []
        for env in self.__environment:
            # Add circle for environment object
            cv2.circle(img, env.get_position(), env.get_radius(), 255)

            # Identify circle using mask
            points = numpy.transpose(numpy.where(img == 255))
            env_points.append(points)

        for point in sensor_points:
            # Loop over sensor points
            for env in env_points:
                # Loop over environment objects
                for env_point in env:
                    if (point[0] == env_point[0]) and (point[1] == env_point[1]):
                        # If sensor point is in the environment points list return True - I apologise to the processor
                        return True

        # Not in range of any environment objects
        return False


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

                        if in_range:
                            # Sensor detected something, log this to be returned at the end of the tick
                            data["sensors"].append({sensor.get_name() : True})
                    elif sensor.get_sub_type() == SensorTypes.CONE:
                        # Simulate conical sensor around bot
                        try:
                            in_range = self.cone_sensor(bot, sensor);
                        except AttributeError:
                            break;

                        if in_range:
                            # Sensor detected something, log this to be returned at the end of the tick
                            data["sensors"].append({sensor.get_name() : True})
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
