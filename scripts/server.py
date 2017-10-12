# Import libraries
import threading
import socketserver
import socket
import cv2
import numpy as np
import math

# Config vars
log_enabled = False
server_ip = '192.168.1.235'
server_port_camera = 8000
server_port_ultrasonic = 8001

# Video configuration
image_fps = 24 
image_width = 640
image_height = 480
image_height_half = int( image_height / 2 )

# Global var (ultrasonic_data) to measure object distances (distance in cm)
ultrasonic_sensor_distance = ' '
ultrasonic_stop_distance = 25
ultrasonic_text_position = ( 16, 16 )

# Other vars
color_blue = (211, 47, 47)
color_yellow = (255, 238, 88)
color_red = (48, 79, 254)
color_green = (0, 168, 0)

# Font used in opencv images
image_font = cv2.FONT_HERSHEY_PLAIN
image_font_size = 1.0
image_font_stroke = 2


# Datos para lineas de control visual. Array stroke_lines contiene 3 componentes:
#   0: Punto inicial (x,y)
#   1: Punto final (x,y)
#   2: Color de linea
#   3: Ancho de linea en px
# Para activarlo/desactivarlo: stroke_enable = True|False
stroke_enabled = True
stroke_width = 4
stroke_lines = [
   [ (0,image_height), ( int( image_width * 0.25 ), int( image_height/2 ) ), color_green, stroke_width ],
   [ (image_width,image_height), ( int( image_width * 0.75 ), int( image_height/2 ) ), color_green, stroke_width ]
];


# Class to handle data obtained from ultrasonic sensor
class StreamHandlerUltrasonic(socketserver.BaseRequestHandler):

    data = ' '

    def handle(self):
        global ultrasonic_sensor_distance
        distance_float = 0.0

        try:
            print( 'Ultrasonic sensor measure: Receiving data in server!' )
            while self.data:
                self.data = self.request.recv(1024)
                try:
                    distance_float = float( self.data )
                except ValueError: 
                    # No es float... porque hemos recibido algo del tipo b'123.123456.456' (es decir, por lag de la red
                    # o sobrecarga de nuestro sistema hemos recibido dos valores antes de ser capaces de procesarlo)
                    distance_float = 1000.0
                
                ultrasonic_sensor_distance = round( distance_float, 1)
                if log_enabled: print( 'Ultrasonic sensor measure received: ' + str( ultrasonic_sensor_distance ) + ' cm' )
 
        finally:
            print( 'Connection closed on ultrasonic thread' )


# Class to handle the jpeg video stream received from client
class StreamHandlerVideocamera(socketserver.StreamRequestHandler):
  
    def handle(self):
        stream_bytes = b' '
        global ultrasonic_sensor_distance

        # stream video frames one by one
        try:
            print( 'Videocamera: Receiving images in server!' )
            while True:
                stream_bytes += self.rfile.read(1024)

                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')
                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last+2]
                    stream_bytes = stream_bytes[last+2:]
                    gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    # lower half of the image
                    half_gray = gray[image_height_half:image_height, :]

                    # Dibujamos lineas "control"
                    if stroke_enabled:
                        for stroke in stroke_lines:
                            cv2.line( image, stroke[0], stroke[1], stroke[2], stroke[3])


                    # Check ultrasonic sensor data (distance to objects in front of the car)
                    if ultrasonic_sensor_distance is not None and ultrasonic_sensor_distance < ultrasonic_stop_distance:
                        cv2.putText( image, 'OBSTACLE ' + str( ultrasonic_sensor_distance ) + 'cm', ultrasonic_text_position, image_font, image_font_size, color_red, image_font_stroke, cv2.LINE_AA)
                        if log_enabled: print( 'Stop, obstacle in front! >> Measure: ' + str( ultrasonic_sensor_distance ) + 'cm - Limit: '+ str(ultrasonic_stop_distance ) + 'cm' )
                    else:
                        cv2.putText( image, 'NO OBSTACLE ' + str( ultrasonic_sensor_distance ) + 'cm', ultrasonic_text_position, image_font, image_font_size, color_green, image_font_stroke, cv2.LINE_AA)

                    # Show images
                    cv2.imshow('image', image)
                    cv2.imshow('mlp_image', half_gray)
    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        finally:
            cv2.destroyAllWindows()
            print( 'Connection closed on videostream thread' )


# Class to handle the different threads 
class ThreadServer( object ):

    # Server thread to handle the video
    def server_thread_camera(host, port):
        print( '+ Starting videocamera stream server in ' + str( host ) + ':' + str( port ) )
        server = socketserver.TCPServer((host, port), StreamHandlerVideocamera)
        server.serve_forever()

    # Server thread to handle ultrasonic distances to objects
    def server_thread_ultrasonic(host, port):
        print( '+ Starting ultrasonic stream server in ' + str( host ) + ':' + str( port ) )
        server = socketserver.TCPServer((host, port), StreamHandlerUltrasonic)
        server.serve_forever()

    print( '+ Starting server - Logs ' + ( log_enabled and 'enabled' or 'disabled'  ) )
    thread_ultrasonic = threading.Thread( name = 'thread_ultrasonic', target = server_thread_ultrasonic, args = ( server_ip, server_port_ultrasonic ) )
    thread_ultrasonic.start()
    
    thread_videocamera = threading.Thread( name = 'thread_videocamera', target = server_thread_camera, args = ( server_ip, server_port_camera ) )
    thread_videocamera.start()



# Starting thread server handler
if __name__ == '__main__':
    ThreadServer()
