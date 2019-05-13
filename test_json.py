import socket, json, struct
import serial
import signal
import sys
import errno

MAX_SPEED = 1000
weights_left = [-10, -10, -5, 0, 0, 5, 10, 10]
weights_right = [-1 * x for x in weights_left]

print weights_left
print weights_right

ser = serial.Serial('/dev/ttyS2', 230400)

# Set up socket 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Arbitrary port number
port = 12345

# Set up socket to listen on localhost with port specified above
# s.bind(('', port))
# s.listen(5)
s.connect(('192.168.100.101', port))

# Set socket to non-blocking -- Prevents locking the robot up
s.setblocking(0)

# Register signal handler for Ctrl+C
def signal_handler(sig, frame):
	print('Ctrl+C pressed')
	ser.write('D,0,0\r\n') # Stop motors
	ser.readline() # Gobble up output
	ser.close()
	s.close() # Close socket when exiting
	sys.exit(0)

def msg_length():
        data = read(4)
        print(data)
        size = struct.unpack('=I', data)
        return size[0]

def read(size):
        data = ''
        print("Size: %d" % size)
        
        while len(data) < size:
                dataTmp = s.recv(size - len(data))
                data += dataTmp

                if dataTmp == '':
                        raise RuntimeError("Connection broken")

        return data

def get_data():
        size = msg_length()
        
        if size > 1024:
                return
        
        data = read(size)

        frmt = "=%ds" % size

        msg = struct.unpack(frmt, data)

        return json.loads(msg[0])

signal.signal(signal.SIGINT, signal_handler)

ser.write('K\r\n') # Calibrate proximity sensors
ser.readline() # Gobble up output
ser.readline() # Gobble up output
ser.write('D,0,0\r\n')
ser.readline() # Gobble up output
# try:
# 	# Try to accept a connection request (exception caught if none present)
# 	c, addr = s.accept()
# 	s.setblocking(0)
# except socket.error:
# 	pass

counter = 0
while True:

	angle = 0

	data = ""

	# Receive data to process
	# data = c.recv(1024)
	try:
        	data = get_data()
        except IOError as e:
                if e.errno == errno.EWOULDBLOCK:
                        pass

	if data != "" and data is not None:
		print(data)
##		data = data.decode('utf-8')
##		print(data)
##		data = json.loads(data)
##		print(data)

		angle = float(data["circle_sensor"])
		print(angle)

	counter += 1

        print("Test: {0}".format(counter))

	ser.write('N\r\n')  # Request IR sensor readings
	ir = ser.readline() # Get IR sensor reading string
	ir = ir.split(',')  # Parse delimited string
	ir = ir[1:9]        # Extract IR readings
	ir = map(int, ir)   # Convert characters to integers
	# print ir

	# left = right = 400

	# # Obstacle avoidance
	# for i, reading in enumerate(ir):
	# 	left += weights_left[i] * reading
	# 	right += weights_right[i] * reading

	# if left > MAX_SPEED:
	# 	left = MAX_SPEED
	# elif left < -MAX_SPEED:
	# 	left = -MAX_SPEED

	# if right > MAX_SPEED:
	# 	right = MAX_SPEED
	# elif right < -MAX_SPEED:
	# 	right = -MAX_SPEED

	#test
	MAX_SPEED = 500

	left = right = MAX_SPEED

	if(angle > 5):
		left = MAX_SPEED
		right = MAX_SPEED / 8
	elif(angle < -5):
		left = MAX_SPEED / 8
		right = MAX_SPEED

	ser.write('D,' + str(left) + ',' + str(right) + '\r\n') # Set wheel speeds
	ser.readline() # Gobble up output
