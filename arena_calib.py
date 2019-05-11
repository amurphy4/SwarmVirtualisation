from SwarmTracking import TrackingController

import cv2

class ArenaCalib():

    def __init__(self, callback):

        self.tc = TrackingController.getInstance()

        self.corners = []

        self.calib_callback = callback

        self.start()

    def callback(self, tags, frame):
        # Reset corners array to account for multiple frames
        self.corners = []
        
        for tag in tags:
            if tag.get_id() == 49:
                # This is one of the corners
                tl, tr, br, bl = tag.get_corners()

                # Calculate centre of the tag
                centre = (int((tl.x + tr.x + br.x + bl.x) / 4), int((tl.y + tr.y + br.y + bl.y) / 4))

                # Add to corners array
                self.corners.append(centre)

        cv2.imshow("Frame", frame)

        if cv2.waitKey(30) > 0:
            cv2.destroyAllWindows()
            self.stop()

    def start(self):
        self.tc.set_callback(self.callback)

        self.tc.start()

    def stop(self):
        self.tc.stop()

        self.calib_callback(self.corners)
