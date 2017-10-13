# Import libraries
import io
import socket
import struct
import time
import picamera


# Config vars
server_ip = '192.168.1.235'
server_port = 8000
image_width = 320
image_height = 240
image_fps = 10
recording_time = 600


# Connect a client socket to server_ip:server_port
print( 'Trying to connect to streaming server in ' + str( server_ip ) + ':' + str( server_port ) );

# create socket and bind host
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
connection = client_socket.makefile('wb')

try:
    with picamera.PiCamera() as camera:
        camera.resolution = (image_width, image_height)
        camera.framerate = image_fps

        # Give 2 secs for camera to initilize
        time.sleep(2)                       
        start = time.time()
        stream = io.BytesIO()
        
        # send jpeg format video stream
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.read())
            if time.time() - start > recording_time:
                break
            stream.seek(0)
            stream.truncate()
    connection.write(struct.pack('<L', 0))

finally:
    connection.close()
    client_socket.close()
    print( 'JPEG streaming finished!' );

