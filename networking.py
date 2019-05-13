import socket, json, time, struct

class Networking():

    def __init__(self):

        self.__port = 12345
        self.__sockets = []

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(0)
        
        self.s.bind(('', self.__port))
        self.s.listen(5)

        self.counter = 0

        #self.connect("192.168.100.200")

    def listen(self):
        try:
            c, addr = self.s.accept()
            c.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.__sockets.append(c)
            return False
        except socket.error:
            return True

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

    def send_data(self, addr, data):
        socket = self.get_socket(addr)
        self.counter += 1

        if self.counter % 25 == 0:
            print(self.counter)
            if socket is None:
                print("Socket is None")
                return

            print("Sending data: {0}".format(self.counter / 10))

            for obj in self.encode_json(data):
                print("Size: %d" % len(obj))
                sent = 0
                while sent < len(data):
                    sent += socket.send(obj[sent:])

    def encode_json(self, data):
        msg = json.dumps(data)
        frmt = "=%ds" % len(msg)

        packedMsg = struct.pack(frmt, msg)
        packedHdr = struct.pack('=I', len(packedMsg))

        print(packedHdr, packedMsg)
                                
        return (packedHdr, packedMsg)

    def close(self):
        for socket in self.__sockets:
            socket.close()

def main(net):
    loop = True

    while loop:
        loop = net.listen() 

    s = net.get_socket("192.168.100.200")

    net.send_data(s, {"circle_sensor" : 64.0973})

    js = json.dumps({"circle_sensor" : 64.0973})

    print(json.loads(js))

    i = 0
    while True:
        i += 1
        print(i)
        net.send_data(s, {"circle_sensor" : 64.0973})

    net.close() 
        
if __name__ == "__main__":
    # TESTING
    net = Networking()

    try:
        main(net)
    except Exception as e:
        print(e)
        net.close()

