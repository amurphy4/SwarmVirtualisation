import socket, json

class Networking():

    def __init__(self):

        self.__port = 12345
        self.__sockets = []

        # TEMP - Testing sockets
        self.connect("192.168.100.104")
        self.connect("192.168.100.101")

    def connect(self, addr):
        s = socket.socket()

        try:
            s.connect((addr, self.__port))
        except socket.error:
            # Connection refused
            s = None

        if s is not None:
            self.__sockets.append(s)
            return True
        else:
            return False

    def get_socket(self, addr):
        for socket in self.__sockets:
            if socket.getpeername()[0] == addr:
                return socket

    def send_data(self, socket, data):
        if socket is None:
            return
        
        socket.send(self.encode_json(data))

    def encode_json(self, data):
        return json.dumps(data)

    def close(self):
        for socket in self.__sockets:
            socket.close()

        
if __name__ == "__main__":
    # TESTING
    net = Networking()

    s = net.get_socket("192.168.100.101")

    net.send_data(s, "Hi!")

    s = net.get_socket("192.168.100.104")

    net.send_data(s, {"Message" : "69.4"})

    net.close()

