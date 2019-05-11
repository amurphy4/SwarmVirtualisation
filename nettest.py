import socket, json

# Set up socket 
s = socket.socket()

# Arbitrary port number
port = 12345

# Set up socket to listen on localhost with port specified above
s.bind(('', port))
s.listen(5)

# Set socket to non-blocking -- Prevents locking the robot up
s.setblocking(0)

# Main loop
while True:
    try:
        # Try to accept a connection request (exception caught if none present)
        c, addr = s.accept()

        # Receive data to process
        data = c.recv(1024)

        data = json.loads(data)

        print(data["Message"])
    except socket.error:
        pass

# Close socket when exiting
s.close()
