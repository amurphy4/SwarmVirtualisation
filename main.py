import sys, cv2

from SwarmTracking import TrackingController
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from enums import *
from environment import *

qt_creator_file = "main_window.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

class SwarmVirtualisation(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.__tc = TrackingController()

        # Simulation objects
        self.__bots = []
        self.__sensors = []
        self.__actuators = []
        self.__environment = []

        # Connect signal for callback - kick back to GUI thread
        self.connect(self, SIGNAL("tracking_callback"), self.tracking_handler)

        # Create testing environment objects
        obj = Environment("food", EnvironmentTypes.GOAL, (300, 300), 10)
        self.__environment.append(obj)

        self.start_tracking()

    def tracking_callback(self, bots, frame):
        # Emit signal for callback - kick back to GUI thread
        self.emit(SIGNAL("tracking_callback"), bots, frame)

    def tracking_handler(self, bots, frame):
        # Update bots with new positions etc.
        for bot in bots:
            for advanced_bot in self.__bots:
                if bot.get_id == advanced_bot.get_id:
                    # This is the bot that needs updating
                    advanced_bot.set_corners(bot.get_corners)

        # Augment frame before converting
        frame = cv2.circle(frame, self.__environment[0].get_position(), self.__environment[0].get_radius(), (0, 255, 0), -1)

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

    def virtualisation_callback(self):
       # Handle sensor and actuator data returned here
       pass

    def start_virtualisation(self):
        self.output_to_console("Starting sensor and actuator virtualisation")

        # Set virtualisation callback function

        # Start virtualisation thread

    def stop_virtualisation(self):
        self.output_to_console("Stopping sensor and actuator virtualisation")

        # Stop virtualisation thread

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
