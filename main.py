### Python libraries ###
import sys, numpy, math, Queue, threading, time

### OpenCV 4.0 required - pip install opencv-contrib ###
import cv2

### SwarmTracking module required - https://github.com/amurphy4/SwarmTracking ###
from SwarmTracking import TrackingController

### Application specific classes ###
from enums import *
from environment import *
from advanced_bot import *
from sensor import *
from simulator import *
from networking import *
from arena_calib import *

frames = Queue.Queue(10)

class SwarmVirtualisation(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        global frames
        print(threading.current_thread().name)
        
        self.__tc = TrackingController.getInstance()
        print(1)
        self.__simulator = Simulator()
        print(2)
        self.__net = Networking()
        print(3)

        self.__queue = Queue.Queue()
        print(4)

        print(threading.current_thread().name)

        # Simulation objects
        self.__bots = []
        self.__sensors = []
        self.__actuators = []
        self.__environment = []
        self.arena_corners = []
        self.arena_centre = (0, 0)

        self.block = True
        self.__exit = False
        self.__calibrated = False

        self.__frame = None

        self.__tag_offset = 0
        self.__tc.set_tag_offset(self.__tag_offset)

        self.start_tracking()
        #self.start_virtualisation()


    def run(self):
        global frames
        print("run")
        while not self.__exit:
##            try:
            bots, frame = self.__queue.get()

            self.tracking_handler(bots, frame)
                #self.set_camera_frame(frame)
                
                
##            except Exception as e:
##                print(e)

    def generate_objects(self):
        print("Generating objects")
        # Create testing environment objects
        obj = Environment("food", EnvironmentTypes.GOAL, self.arena_centre, 10)
        self.__environment.append(obj)

        # Create testing sensor objects
        sensor = Sensor("food_sensor", SensorTypes.CIRCLE, radius=50)
        self.__sensors.append(sensor)
        sensor = Sensor("test_sensor", SensorTypes.CONE, radius=50, angle_offset=0, cone_angle=75)
        self.__sensors.append(sensor)
        sensor = Sensor("line_sensor", SensorTypes.LINE, _range=50, angle_offset=90)
        self.__sensors.append(sensor)

    def tracking_callback(self, bots, frame):
        print("callback {0}".format(threading.current_thread().name))
        self.__queue.put((bots, frame))
        print(self.__queue.qsize())

    def tracking_handler(self, bots, frame):
        print("handler {0}".format(threading.current_thread().name))
        self.__frame = frame

        for bot in self.__bots:
            # Set all bots to invisible so we don't see sensors for bots the system has lost track of
            bot.set_is_visible(False)

        corners = []
        
        # Update bots with new positions etc.
        for bot in bots:

            # Reset bot_found flag to check if the bot exists in our environment yet
            bot_found = False
            
            for advanced_bot in self.__bots:
                # Loop over bots in our environment searching for the bot to update
                if bot.get_id() == advanced_bot.get_id():
                    # This is the bot that needs updating
                    tr, tl, bl, br = bot.get_corners()
                    advanced_bot.set_corners(tr, tl, bl, br)

                    # We found the bot, no need to add it to the list - make visible again
                    bot_found = True
                    advanced_bot.set_is_visible(True)

            if not bot_found:
                if bot.get_id() == 49 and self.__calibrated:
                    print(bot)
                    continue
                elif bot.get_id() == 49:
                    # Get corners
                    tl, tr, br, bl = bot.get_corners()

                    print(bot.get_corners())

                    # Calculate centre of the tag
                    centre = (int((tl.x + tr.x + br.x + bl.x) / 4), int((tl.y + tr.y + br.y + bl.y) / 4))

                    # Add to corners array
                    corners.append(centre)

                    continue
                
                # We didn't find the bot - create a new one in our environment
                new_bot = Bot(bot)

                # Add all the sensors <-- testing purposes only
                #new_bot.add_sensor(self.__sensors[0].copy())
                #new_bot.add_sensor(self.__sensors[1].copy())
                #new_bot.add_sensor(self.__sensors[2].copy())

                # Set sensor for bot 5 to be visible
##                if new_bot.get_id() == 5:
##                    new_bot.get_sensors()[0].set_is_visible(True)
                    
                # We've created a bot! Add it to our environment!
                self.__bots.append(new_bot)
                
        self.arena_corners = corners

        # Augment frame before converting
        # Add environment objects to overlay
        overlay = frame.copy()
        for env in self.__environment:
            print("Env overlay added at ", env.get_position())
            overlay = cv2.circle(overlay, env.get_position(), env.get_radius(), (0, 255, 0), -1)
        
        # Add sensors to overlay
        for bot in self.__bots:
            if bot.get_is_visible():
                for sensor in bot.get_sensors():
                    if sensor.get_is_visible():
                        if sensor.get_sub_type() == SensorTypes.CIRCLE:
                            # Draw circle
                            cv2.circle(overlay, (bot.get_centre().x, bot.get_centre().y), sensor.get_radius(), (0, 255, 0), -1)
                        elif sensor.get_sub_type() == SensorTypes.CONE:
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
                            cv2.ellipse(overlay, (centre.x, centre.y), (radius, radius), 0, start_angle, end_angle, (0, 255, 0), -1)
                        elif sensor.get_sub_type() == SensorTypes.LINE:
                            # Get positions from bot
                            centre = bot.get_centre()
                            front = bot.get_front_point()

                            # Calculate distance between top and centre of tag - used for scaling sensor end coords
                            a = numpy.array((front.x, front.y))
                            b = numpy.array((centre.x, centre.y))
                            dist = numpy.linalg.norm(a - b)

                            # Calculate a scaling factor 
                            scale_factor = float(sensor.get_range()) / float(dist)

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
                            cv2.line(overlay, (centre.x, centre.y), end, 255, 5)
                            
        # Transparency for overlaid augments
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Convert frame and show in GUI
        self.set_camera_frame(frame)

    def set_camera_frame(self, frame):
        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1)

        if key == ord('q'):
            print("Destroying")
            cv2.destroyAllWindows()
            self.stop_tracking()
            self.__exit = True
        elif key == ord('r'):
            # Run experiments
            pass
        elif key == ord('c'):
            # Calibrate
            print("Calibrating...")
            x = 0
            y = 0
            for corner in self.arena_corners:
                print("corner found")
                x = x + corner[0]
                y = y + corner[1]

            self.arena_centre = (int(x / 4), int(y / 4))
            print(self.arena_centre)
            self.__calibrated = True
            self.generate_objects()

    def output_to_console(self, message):
        pass

    def virtualisation_callback(self, data):
       # Handle sensor and actuator data returned here
       #print(data)
##       socket = self.__net.get_socket("BOT IP ADDRESS")
##       self.__net.send_data(socket, data)
       pass

    def environment_callback(self, env, destroy=None):
        if destroy:
            self.__environment.remove(env)
        else:
            self.__environment.append(env)

    def simulator_data(self):
        return self.__bots, self.__environment, self.__frame

    def start_virtualisation(self):
        self.output_to_console("Starting sensor and actuator virtualisation")

        # Set virtualisation callback function
        self.__simulator.set_callback(self.virtualisation_callback)

        self.__simulator.set_data_method(self.simulator_data)

        self.__simulator.set_interaction(self.environment_callback)

        # Start virtualisation thread
        self.__simulator.start()

    def stop_virtualisation(self):
        self.output_to_console("Stopping sensor and actuator virtualisation")

        # Stop virtualisation thread
        self.__simulator.stop()

    def start_tracking(self):
        self.output_to_console("Starting swarm tracking")

        # Set tracking callback function
        self.__tc.set_callback(self.tracking_callback)

        # Start tracking thread
        self.__tc.start()

    def stop_tracking(self):
        self.output_to_console("Stopping swarm tracking. This will also stop virtualisation")

        # Stop tracking thread
        self.__tc.stop()

        # Stop virtualisation - no point keeping this going with no new incoming image
        self.stop_virtualisation()

        # Set camera label text to inform user they need to restart the tracking thread to view camera images
        #self.camera_label.setText("Start tracking to restart the live camera")

    def load_sensors(self):
        # Load sensor definitions from file
        pass

    def load_actuators(self):
        # Load actuator definitions from file
        pass

    def closeEvent(self, event):
        # Reimplement close event to quit threads on exit
        self.stop_tracking()

class ImageGrabber(threading.Thread):
    def __init__(self, ID):
        threading.Thread.__init__(self)
        self.ID=ID
        self.cam=cv2.VideoCapture(ID)
        print("Camera opened")

    def run(self):
        print("Camera running")
        global frames
        while True:
            ret,frame=self.cam.read()
            print("Frames")
            frames.put(frame)
            time.sleep(0.1)

arena_corners = []
block = True

def calib_callback(corners):
    global block
    global arena_corners
    arena_corners = corners
    block = False
    print("Unblocking")

def main():
##    calib = ArenaCalib(calib_callback)
##
##    while block:
##        pass

    print("main")
    window = SwarmVirtualisation()
    print("Start thread")
    window.start()

    window.join()
    #grabber.join()

if __name__ == "__main__":
    main()
