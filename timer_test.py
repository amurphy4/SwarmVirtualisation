import threading, sys

timer = None

def callback():
    print("Callback!")

def main():
    global timer
    timer = threading.Timer(10.0, callback)
    timer.start()

if __name__ == "__main__":
    main()
