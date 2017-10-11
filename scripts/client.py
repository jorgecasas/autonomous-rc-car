# Importamos librerias RPi.GPIO (entradas/salidas GPIO de Raspberry Pi) y time (para sleeps, etc...)
# Requiere previamente instalarla (pip install RPi.GPIO)
import RPi.GPIO as GPIO
import time
import io
import socket
import struct
import picamera

# Configure Raspberry Pi GPIO in BCM mode
GPIO.setmode(GPIO.BCM) 


# Config vars. These IP and ports must be available in server firewall
server_ip = '192.168.1.235'
server_port_ultrasonic = 8001
server_port_camera = 8000
image_width = 320
image_height = 240
image_fps = 10
recording_time = 600

# Definition of GPIO pins in Raspberry Pi 3 (GPIO pins schema needed!)
#   18 - Trigger (output)
#   24 - Echo (input)
GPIO_ultrasonic_trigger = 18
GPIO_ultrasonic_echo = 24

# Class to handle the ultrasonic sensor stream in client
class StreamClientUltrasonic():
  
    def __init__(self):

        # Connect a client socket to server_ip:server_port_ultrasonic
        print( 'Trying to connect to ultrasonic streaming server in ' + str( server_ip ) + ':' + str( server_port_ultrasonic ) );

        # Configure GPIO pins (trigger as output, echo as input)
        GPIO.setup( GPIO_ultrasonic_trigger, GPIO.OUT )
        GPIO.setup( GPIO_ultrasonic_echo, GPIO.IN )

        # Set output GPIO pins to False
        GPIO.output( GPIO_ultrasonic_trigger, False ) 

        # Create socket and bind host
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect( ( server_ip, server_port_ultrasonic ) )

        try:
            while True:
                # Measure and send data to the host every 0.25 sec, 
                # pausing for a while to no lock Raspberry Pi processors
                distance = measure()
                print( "Distance : %.1f cm" % distance )
                client_socket.send( str( distance ) )
                time.sleep( 0.25 )

        finally:
            # Ctrl + C to exit app (cleaning GPIO pins and closing socket connection)
            print( 'Ultrasonic sensor stopped' )
            client_socket.close()
            GPIO.cleanup()

    def measure():
        # Measure distance from ultrasonic sensor. Send a trigger pulse
        GPIO.output( GPIO_ultrasonic_trigger, True )
        time.sleep( 0.00001 )
        GPIO.output( GPIO_ultrasonic_trigger, False )
        
        # Get start time
        start = time.time()

        # Wait to receive any ultrasound in sensor (echo)
        while GPIO.input( GPIO_ultrasonic_echo ) == 0:
            start = time.time()

        # We have received the echo. Wait for its end, getting stop time
        while GPIO.input( GPIO_ultrasonic_echo ) == 1:
            stop = time.time()

        # Calculate time difference. Sound has gone from trigger to object and come back to sensor, so 
        # we have to divide between 2. Formula: Distance = ( Time elapsed * Sound Speed ) / 2 
        time_elapsed = stop-start
        distance = (time_elapsed * 34300) / 2

        return distance


# Class to handle the jpeg video stream in client
class StreamClientVideocamera():
  
    def __init__(self):

        # Connect a client socket to server_ip:server_port_camera
        print( 'Trying to connect to videocamera streaming server in ' + str( server_ip ) + ':' + str( server_port_camera ) );

        # create socket and bind host
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port_camera))
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




 

# Class to handle the different threads in client 
class ThreadClient():

    # Client thread to handle the video
    def client_thread_camera(host, port):
        StreamClientVideocamera()

    # Client thread to handle ultrasonic distances to objects
    def client_thread_ultrasonic(host, port):
        StreamClientUltrasonic()

    print( '+ Starting videocamera stream client in ' + str( server_ip ) + ':' + str( server_port_camera ) )
    thread_videocamera = threading.Thread(target=client_thread_camera( server_ip, server_port_camera ) )
    thread_videocamera.start()

    print( '+ Starting ultrasonic stream client in ' + str( server_ip ) + ':' + str( server_port_ultrasonic ) )
    thread_ultrasonic = threading.Thread(target=client_thread_ultrasonic( server_ip, server_port_ultrasonic ) )
    thread_ultrasonic.start()


# Starting thread client handler
if __name__ == '__main__':
    ThreadClient( server_ip, server_port_camera, server_port_ultrasonic )
