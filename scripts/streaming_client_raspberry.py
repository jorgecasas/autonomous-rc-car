# Import libraries
import socket
import time
import picamera

# Config vars
server_ip = '192.168.1.235'
server_port = 8000
image_width = 320
image_height = 240
image_fps = 24
recording_time = 60


# Connect a client socket to my_server:8000
# (change my_server to the hostname of your server)
client_socket = socket.socket()
client_socket.connect(( server_ip, server_port))

# Make a file-like object out of the connection
print 'Trying to connect to streaming server in ' + str( server_ip ) + ':' + str( server_port );

connection = client_socket.makefile('wb')

try:
    camera = picamera.PiCamera()
    camera.resolution = (image_width, image_height)
    camera.framerate = image_fps
    
    # Start a preview and let the camera warm up
    camera.start_preview()
    time.sleep(2)
    
    # Start recording, sending the output to the connection for 60
    # seconds, then stop
    camera.start_recording(connection, format='h264')
    camera.wait_recording( recording_time )
    camera.stop_recording()

finally:
    connection.close()
    client_socket.close()
    print 'Connection to streaming server has finished'
