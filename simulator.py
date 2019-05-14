import cv2, numpy, threading, math, time

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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
        self.__tag_offset = None

        self.__callback = None
        self.__data_method = None
        self.__interaction = None

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

    def set_interaction(self, method):
        self.__interaction = method

    def get_data(self):
        self.__bots, self.__environment, self.__frame, self.__tag_offset = self.__data_method()

    def angle(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2

        dot = x1 * x2 + y1 * y2

        len1 = math.hypot(x1, y1)
        len2 = math.hypot(x2, y2)

        return math.degrees(math.acos(dot / (len1 * len2)))

    def circle_sensor(self, bot, sensor):
        point1 = Point(bot.get_centre().x, bot.get_centre().y)

        circle = point1.buffer(sensor.get_radius())

        env_points = []

        # Identify points for all environment objects 
        for env in self.__environment:
            point2 = Point(env.get_position()[0], env.get_position()[1])
            a = numpy.array(env.get_position())
            b = numpy.array((bot.get_centre().x, bot.get_centre().y))
            dist = numpy.linalg.norm(a - b)

            if dist < sensor.get_radius():
                front = bot.get_front_point()
                centre = bot.get_centre()
                p1 = (front.x - centre.x, front.y - centre.y)
                p2 = (env.get_position()[0] - centre.x, env.get_position()[1] - centre.y)

                atan = math.degrees(math.atan2(p1[1], p1[0]) - math.atan2(p2[1], p2[0]))

                if atan > 180:
                    atan = atan - 360
                elif atan < -180:
                    atan = atan + 360

                atan = -atan

                return atan

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
        cv2.ellipse(img, (centre.x, centre.y), (radius, radius), 0, start_angle, end_angle, 255) - 90 + self.__tag_offset

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
                        front = bot.get_front_point()
                        centre = bot.get_centre()
                        p1 = (front.x - centre.x, front.y - centre.y)
                        p2 = (point[1] - centre.x, point[0] - centre.y)

                        atan = math.degrees(math.atan2(p1[1], p1[0]) - math.atan2(p2[1], p2[0]))

                        if atan > 180:
                            atan = atan - 360

                        atan = -atan

                        print(atan)

                        return atan

        # Not in range of any environment objects
        return False


    def line_sensor(self, bot, sensor):
        height = self.__frame.shape[0]
        width = self.__frame.shape[1]

        # Create blank mask
        img = numpy.zeros((height, width), numpy.uint8)
        
        # Get positions from bot
        centre = bot.get_centre()
        front = bot.get_front_point()

        # Calculate distance between top and centre of tag - used for scaling sensor end coords
        a = numpy.array((front.x, front.y))
        b = numpy.array((centre.x, centre.y))
        dist = numpy.linalg.norm(a - b)

        # Calculate a scaling factor 
        scale_factor = float(sensor.get_range() + self.__tag_offset) / float(dist)

        # Transform around centre as origin point
        front.x = front.x - centre.x
        front.y = front.y - centre.y

        # Scale coordinates
        end = (int(float(front.x) * scale_factor), int(float(front.y) * scale_factor))

        # Rotate end coords around centre by theta degrees
        theta = math.radians(sensor.get_angle_offset())

        endX = int(end[0] * math.cos(theta) - end[1] * math.sin(theta))
        endY = int(end[0] * math.sin(theta) + end[1] * math.cos(theta))

        end = (endX, endY)

        # Transform back
        end = (end[0] + centre.x, end[1] + centre.y)

        # Add sensor to image
        cv2.line(img, (centre.x, centre.y), end, 255, 5)

        # Get points in sensor
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
                        return sensor.get_angle_offset()

        # Not in range of any environment objects
        return False

    def placer(self, bot, actuator):
        if len(actuator.get_inventory() > 0):
            # Place inventory item
            self.__interaction(actuator.get_inventory()[0])
            actuator.get_inventory().pop(0)
            return True
        else:
            ticks_per_place = actuator.get_ticks_per_place()
            ticks = actuator.get_ticks()

            if ticks == ticks_per_place:
                # Place item at current position
                obj = bot.get_obj_to_place().copy()
                obj.set_position((bot.get_centre().x, bot.get_centre().y))
                self.__interaction(obj)
                
                bot.reset_ticks()

                return True
            else:
                bot.increment_ticks()

                return False

    def grabber(self, bot, actuator):
        centre = bot.get_centre()
        tl, tr, br, bl = bot.get_corners()

        # Identify points for all environment objects 
        for env in self.__environment:
            # Add circle for environment object
##            cv2.circle(img, env.get_position(), env.get_radius(), 255)
##
##            # Identify circle using mask
##            points = numpy.transpose(numpy.where(img == 255))

            p = Point(env.get_position())
            poly = Polygon([(tl.x, tl.y), (tr.x, tr.y), (br.x, br.y), (bl.x, bl.y)])

            if poly.contains(p):
                env.set_capacity(env.get_capacity() - 1)

                self.__interaction(env, True)

                bot.set_collected(bot.get_collected() + 1)
                    
                return actuator.add_to_inventory(env.copy())
                    

    def _simulate(self):
        while self.__looping:
            #SIMULATE SHIT

            print("Simulation")

            start = time.time()

            self.get_data()

            data = {"bots" : []}

            for bot in self.__bots:
                bot_data = {"id" : bot.get_id(), "sensors" : [], "actuators" : [], "run" : False}
                # Simulate sensors for each bot
                for sensor in bot.get_sensors():
                    # Simulate sensor
                    if sensor.get_sub_type() == SensorTypes.CIRCLE:
                        # Simulate fully circular sensor around bot
                        try:
                            angle = self.circle_sensor(bot, sensor);
                        except AttributeError as e:
                            print(e)
                            continue
                        
                        # Sensor detected something, log this to be returned at the end of the tick
                        bot_data["sensors"].append({sensor.get_name() : angle})
                    elif sensor.get_sub_type() == SensorTypes.CONE:
                        # Simulate conical sensor around bot
                        try:
                            angle = self.cone_sensor(bot, sensor);
                        except AttributeError:
                            continue

                        # Sensor detected something, log this to be returned at the end of the tick
                        bot_data["sensors"].append({sensor.get_name() : angle})
                    elif sensor.get_sub_type() == SensorTypes.LINE:
                        # Simulate linear sensor around bot
                        try:
                            angle = self.line_sensor(bot, sensor);
                        except AttributeError:
                            continue

                        # Sensor detected something, log this to be returned at the end of the tick
                        bot_data["sensors"].append({sensor.get_name() : angle})

                

                for actuator in bot.get_actuators():
                    if actuator.get_sub_type() == ActuatorTypes.PLACER:
                        placed = self.placer(bot, actuator)
                        
                        if placed:
                            bot_data["actuators"].append({actuator.get_name() : {actuator.get_sub_type() : True}})
                    elif actuator.get_sub_type() == ActuatorTypes.GRABBER:
                        try:
                            grabbed = self.grabber(bot, actuator)

                            if grabbed:
                                print(grabbed)
                                bot_data["actuators"].append({actuator.get_name() : {actuator.get_sub_type() : True}})

                        except AttributeError as e:
                            print(e)
                            pass
                        
                data["bots"].append(bot_data)

            end = time.time()

            print("Time: %f" % (end - start))

            self.__callback(data)
                

class SimulationThread(threading.Thread):

    def __init__(self, threadId, name, counter):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.name = name
        self.counter = counter


    def run(self):
        Simulator.getInstance()._simulate()
