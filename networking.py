import socket

s = socket.socket()

port = 12345

s.bind(('', port))
s.listen(5)

while True:
    c, addr = s.accept()

##    c.send("Hello World!")

    try:
        print("Sent 'Hello World!' to {0}".format(addr))
    except Exception:
        print("An error occured displaying connected address")

    c.close()
