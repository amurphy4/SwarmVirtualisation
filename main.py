### Python libraries ###
import sys, numpy, math

### OpenCV 4.0 required - pip install opencv-contrib ###
import cv2

### SwarmTracking module required - https://github.com/amurphy4/SwarmTracking ###
from SwarmTracking import TrackingController

### PyQt4 modules required - sudo apt-get install python-qt4 ###
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

### Application specific classes ###
from enums import *
from environment import *
from advanced_bot import *
from sensor import *
from simulator import *

qt_creator_file = "main_window.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

class SwarmVirtualisation(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.__tc = TrackingController()
        self.__simulator = Simulator()

        # Simulation objects
        self.__bots = []
        self.__sensors = []
        self.__actuators = []
        self.__environment = []

        self.__frame = None

        self.__tag_offset = 45
        self.__tc.set_tag_offset(self.__tag_offset)

        # Connect signal for callback - kick back to GUI thread
        self.connect(self, SIGNAL("tracking_callback"), self.tracking_handler)

        # Create testing environment objects
        obj = Environment("food", EnvironmentTypes.GOAL, (1280, 550), 10)
        self.__environment.append(obj)

        # Create testing sensor objects
        sensor = Sensor("food_sensor", SensorTypes.CIRCLE, radius=50)
        self.__sensors.append(sensor)
        sensor = Sensor("test_sensor", SensorTypes.CONE, radius=50, angle_offset=30)
        self.__sensors.append(sensor)

        self.start_tracking()
        self.start_virtualisation()

    def tracking_callback(self, bots, frame):
        # Emit signal for callback - kick back to GUI thread
        self.emit(SIGNAL("tracking_callback"), bots, frame)

    def tracking_handler(self, bots, frame):
        self.__frame = frame

        for bot in self.__bots:
            # Set all bots to invisible so we don't see sensors for bots the system has lost track of
            bot.set_is_visible(False)
        
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
                # We didn't find the bot - create a new one in our environment
                new_bot = Bot(bot)

                # Add all the sensors <-- testing purposes only
                new_bot.add_sensor(self.__sensors[0].copy())
                new_bot.add_sensor(self.__sensors[1].copy())

                # Set sensor for bot 5 to be visible
                if new_bot.get_id() == 5:
                    new_bot.get_sensors()[0].set_is_visible(True)
                    self.output_to_console('Sensor "{0}" set to visible'.format(new_bot.get_sensors()[0].get_name()))

                # We've created a bot! Add it to our environment!
                self.__bots.append(new_bot)
                self.output_to_console("Discovered bot with ID: {0} at ({1}, {2}). Registering data.".format(new_bot.get_id(), new_bot.get_centre().x, new_bot.get_centre().y))
                self.output_to_console('Added sensor "{0}" to bot with ID: {1}'.format(self.__sensors[0].get_name(), new_bot.get_id()))

        # Augment frame before converting
        # Add environment objects to overlay
        overlay = frame.copy()
        overlay = cv2.circle(overlay, self.__environment[0].get_position(), self.__environment[0].get_radius(), (0, 255, 0), -1)
        
        # Add sensors to overlay
        for bot in self.__bots:
            if bot.get_is_visible():
                for sensor in bot.get_sensors():
                    if sensor.get_is_visible():
                        if sensor.get_sub_type() == SensorTypes.CIRCLE:
                            pass
                            #cv2.circle(overlay, (bot.get_centre().x, bot.get_centre().y), sensor.get_radius(), (0, 255, 0), -1)
                        elif sensor.get_sub_type() == SensorTypes.CONE:
                            front = bot.get_front_point()
                            centre = bot.get_centre()

                            a = numpy.array((front.x, front.y))
                            b = numpy.array((centre.x, centre.y))
                            dist = numpy.linalg.norm(a - b)

                            pointY = centre.y + dist

                            result = math.atan2(pointY - centre.y, centre.x - centre.x) - math.atan2(front.y - centre.y, front.x - centre.x)
                            
                            start_angle = math.degrees(result) - int(sensor.get_angle_offset() / 2)
                            end_angle = start_angle + sensor.get_angle_offset()
                            print("Start: {0}, End: {1}".format(start_angle, end_angle))
                            radius = sensor.get_radius()
                            cv2.ellipse(overlay, (centre.x, centre.y), (radius, radius), 0, start_angle, end_angle, (0, 255, 0), -1)

        # Transparency for overlaid augments
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Convert frame and show in GUI
        self.set_camera_frame(frame)

    def set_camera_frame(self, frame):
        # Convert frame to QImage format
        qtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)

        # Rescale frame
        image = qtFormat.scaled(1280, 720, Qt.KeepAspectRatio)

        # Set camera label with frame
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    def output_to_console(self, message):
        # Output information to the GUI console
        self.txt_console_output.appendPlainText(message)

    def virtualisation_callback(self, data):
       # Handle sensor and actuator data returned here
       #print(data)
       pass

    def simulator_data(self):
        return self.__bots, self.__environment, self.__frame

    def start_virtualisation(self):
        self.output_to_console("Starting sensor and actuator virtualisation")

        # Set virtualisation callback function
        self.__simulator.set_callback(self.virtualisation_callback)

        self.__simulator.set_data_method(self.simulator_data)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SwarmVirtualisation()
    window.show()
    sys.exit(app.exec_())
