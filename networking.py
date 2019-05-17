import socket, json, time, struct

class Networking():

    def __init__(self):

        self.__port = 12345
        self.__sockets = []

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setblocking(0)

        self.time_of_last_packet = time.time()
        
        self.s.bind(('', self.__port))
        self.s.listen(5)

        self.counter = {
            "192.168.100.200" : 0,
            "192.168.100.201" : 0,
            "192.168.100.202" : 0,
            "192.168.100.203" : 0,
            "192.168.100.204" : 0
        }
            

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
            print(socket.getpeername())
            if socket.getpeername()[0] == addr:
                return socket

        print("Socket not found")

    def send_data(self, addr, data):
        valid = False
        for key in self.counter:
            if addr == key:
                valid = True

        if not valid:
            return

        socket = self.get_socket(addr)
        
        self.counter[addr] += 1

        current_time = time.time()

        since_last = current_time - self.time_of_last_packet

        if since_last >= 0.1:
            self.time_of_last_packet = current_time
            if socket is None:
                return

            print("Sending data: {0}".format(data))

            msg = self.encode_json(data)
            sent = 0
            while sent < len(msg):
                sent += socket.send(msg[sent:])

    def encode_json(self, data):
        msg = self.pad_data(json.dumps(data), 512)
        
        return msg

    def pad_data(self, data, length):
        print(data)
        while length > len(data):
            data = data + '@'

        return data

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

