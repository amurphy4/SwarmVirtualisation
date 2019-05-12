import threading
import time
import Queue
import cv2
frames = Queue.Queue(10)

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


class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print("Queue")

    def run(self):
        print("Runnign")
        global frames
        while True:
            if(not frames.empty()):
                self.Currframe=frames.get()
                print("Working")
                cv2.imshow("Test", self.Currframe)
                cv2.waitKey(1)
            ##------------------------##
            ## your opencv logic here ##
            ## -----------------------##


if __name__ == "__main__":
    grabber = ImageGrabber(0)
    main = Main()

    grabber.start()
    main.start()
    main.join()
    grabber.join()
