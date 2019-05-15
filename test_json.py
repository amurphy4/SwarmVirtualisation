import socket, json, struct
import serial
import signal
import sys
import errno

MAX_SPEED = 1000 / 4
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

def stop():
        ser.write('D,0,0\r\n') # Stop motors
	ser.readline() # Gobble up output

def unpad_data(data):
        result = data.split('@')
        return result[0]

def read():
	data = ''
	# print("Size: %d" % size)

	while len(data) < 512:
		dataTmp = s.recv(512)
		data += dataTmp

	if dataTmp == '':
		stop()

	return data

def get_data():
        data = read()

        msg = unpad_data(data)

        print(msg)

	return json.loads(msg)

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
angle = 0
run = False
counter = 0
while True:
        angle = 0
        recv = False
        
	data = ""

	# Receive data to process
	# data = c.recv(1024)
	try:
		data = get_data()
	except IOError as e:
		if e.errno == errno.EWOULDBLOCK:
			pass
	except ValueError as e:
                print(e)

	if data != "" and data is not None:
                try:
                        recv = True
                        print(data)
        ##		data = data.decode('utf-8')
        ##		print(data)
        ##		data = json.loads(data)
        ##		print(data)

                        angle = float(data["sensors"][0]["circle_sensor"])
                        run = data["run"]
                except ValueError as e:
                        print(e)

		print(angle)

	counter += 1

	print(counter)

	# print("Test: {0}".format(counter))

	ser.write('N\r\n')  # Request IR sensor readings
	ir = ser.readline() # Get IR sensor reading string
	ir = ir.split(',')  # Parse delimited string
	ir = ir[1:9]        # Extract IR readings
	ir = map(int, ir)   # Convert characters to integers
	# print ir

	left = right = MAX_SPEED

	avoiding = False

	# Obstacle avoidance
	for i, reading in enumerate(ir):
		if reading > 300:
			avoiding = True
			left += weights_left[i] * reading
			right += weights_right[i] * reading

	if not avoiding:
                if recv:
                        if(angle > 10):
                                left = MAX_SPEED * 2
                                right = -MAX_SPEED * 2
                        elif(angle < -10):
                                left = -MAX_SPEED * 2
                                right = MAX_SPEED * 2

        if not run:
                left = right = 0

	ser.write('D,' + str(left) + ',' + str(right) + '\r\n') # Set wheel speeds
	ser.readline() # Gobble up output
