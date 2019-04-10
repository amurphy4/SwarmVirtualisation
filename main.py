import sys

from SwarmTracking import TrackingController
from PyQt4 import QtCore, QtGui, uic

qt_creator_file = "main_window.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)

class SwarmVirtualisation(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.__tc = TrackingController()

        self.__bots = []

        self.__frame = None

        # TESTING - REMOVE
        self.btn_add_definition.clicked.connect(self.start_virtualisation)

        # Sensor and actuator definitions
        self.__sensors = []
        self.__actuators = []

    def tracking_callback(self, bots, frame):
        # Update bots with new positions etc.
        for bot in bots:
            for advanced_bot in self.__bots:
                if bot.get_id == advanced_bot.get_id:
                    # This is the bot that needs updating
                    advanced_bot.set_corners(bot.get_corners)

        self.__frame = frame

    def virtualisation_callback(self):
       # Handle sensor and actuator data returned here
       pass

    def start_virtualisation(self):
        print("Starting sensor and actuator virtualisation")
        self.txt_console_output.appendPlainText("Starting sensor and actuator virtualisation")

        # Set virtualisation callback function

        # Start virtualisation thread

    def stop_virtualisation(self):
        print("Stopping sensor and actuator virtualisation")

        # Stop virtualisation thread

    def start_tracking(self):
        print("Starting swarm tracking")

        # Set tracking callback function
        self.__tc.set_callback(tracking_callback)

        # Start tracking thread
        self.__tc.start()

    def stop_tracking(self):
        print("Stopping swarm tracking. This will also stop virtualisation")

        # Stop tracking thread
        self.__tc.stop()

        # Stop virtualisation
        self.stop_virtualisation()

    def load_sensors(self):
        # Load sensor definitions from file
        pass

    def load_actuators(self):
        # Load actuator definitions from file
        pass

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = SwarmVirtualisation()
    window.show()
    sys.exit(app.exec_())
