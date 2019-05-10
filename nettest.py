import socket

s = socket.socket()

port = 12345

s.connect(('192.168.100.101', port))

while True:
    print(s.recv(1024))

s.close()
