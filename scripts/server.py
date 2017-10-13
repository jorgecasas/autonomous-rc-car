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
image_gray_enabled = False
image_fps = 24 
image_width = 640
image_height = 480
image_height_half = int( image_height / 2 )

# Global var (ultrasonic_data) to measure object distances (distance in cm)
ultrasonic_sensor_distance = 1000.0
ultrasonic_stop_distance = 25
ultrasonic_text_position = ( 16, 16 )

# Other vars
color_blue = (255, 0, 0)
color_yellow = (0,255,255)
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
stroke_width = 3
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

        # Object detection initialization (STOP sign, traffic light) using cascade classifiers
        self.obj_detection = ObjectDetection()
        self.stop_cascade = cv2.CascadeClassifier('cascade_xml/stop_sign.xml')
        self.light_cascade = cv2.CascadeClassifier('cascade_xml/traffic_light.xml')

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
                    image = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    image_gray = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

                    # Visualization of lower half of the gray image
                    if image_gray_enabled:
                        half_gray = image_gray[image_height_half:image_height, :]

                    # Dibujamos lineas "control"
                    if stroke_enabled:
                        for stroke in stroke_lines:
                            cv2.line( image, stroke[0], stroke[1], stroke[2], stroke[3])

                    # Object detection (STOP sign, traffic light), calculating distances to objects
                    detection_stop = self.obj_detection.detect( self.stop_cascade, image_gray, image )
                    detection_traffic_light = self.obj_detection.detect( self.light_cascade, image_gray, image )

                    if detection_stop > 0:
                        print( 'STOP sign detected!' )
                    elif detection_traffic_light > 0:
                        print( 'Traffic Light detected!' )


                    # Check ultrasonic sensor data (distance to objects in front of the car)
                    if ultrasonic_sensor_distance is not None:
                        if ultrasonic_sensor_distance < ultrasonic_stop_distance:
                            cv2.putText( image, 'OBSTACLE ' + str( ultrasonic_sensor_distance ) + 'cm', ultrasonic_text_position, image_font, image_font_size, color_red, image_font_stroke, cv2.LINE_AA)
                            if log_enabled: print( 'Stop, obstacle in front! >> Measure: ' + str( ultrasonic_sensor_distance ) + 'cm - Limit: '+ str(ultrasonic_stop_distance ) + 'cm' )
                        elif ultrasonic_sensor_distance < 1000.0:
                            cv2.putText( image, 'NO OBSTACLE ' + str( ultrasonic_sensor_distance ) + 'cm', ultrasonic_text_position, image_font, image_font_size, color_green, image_font_stroke, cv2.LINE_AA)
                        else: 
                            cv2.putText( image, 'OBSTACLE DETECTION DISABLED', ultrasonic_text_position, image_font, image_font_size, color_yellow, image_font_stroke, cv2.LINE_AA)

                    # Show images
                    cv2.imshow('image', image)
                    if image_gray_enabled:
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

# Class to detect Traffic Lights and STOP sign using cascade classifiers
class ObjectDetection(object):

    def __init__(self):
        self.red_light = False
        self.green_light = False
        self.yellow_light = False

    def detect(self, cascade_classifier, image_gray, image):

        # y camera coordinate of the target point 'P'
        value = 0

        # Minimum value to proceed traffic light state validation
        threshold = 150     
        
        # Detection
        cascade_obj = cascade_classifier.detectMultiScale(
            image_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # draw a rectangle around the objects
        for (x_pos, y_pos, width, height) in cascade_obj:
            value = y_pos + height - 5

            # STOP sign
            if width/height == 1:
                cv2.putText( image, 'STOP', (x_pos, y_pos), image_font, image_font_size, color_red, image_font_stroke )
                cv2.rectangle( image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), color_red, stroke_width )
            
            # Traffic lights
            else:
                roi = image_gray[y_pos+10:y_pos + height-10, x_pos+10:x_pos + width-10]
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)
                
                # check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)
                    
                    # Red light
                    if 1.0/8*(height-30) < maxLoc[1] < 4.0/8*(height-30):
                        cv2.putText(image, 'Traffic Light RED', (x_pos, y_pos), image_font, image_font_size, color_red, image_font_stroke )
                        cv2.rectangle( image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), color_red, stroke_width )
                        self.red_light = True
                    
                    # Green light
                    elif 5.5/8*(height-30) < maxLoc[1] < height-30:
                        cv2.putText(image, 'Traffic Light GREEN', (x_pos, y_pos), image_font, image_font_size, color_green, image_font_stroke )
                        cv2.rectangle( image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), color_green, stroke_width )
                        self.green_light = True
    
                    # Yellow light
                    elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
                        cv2.putText(image, 'Traffic Light YELLOW', (x_pos, y_pos), image_font, image_font_size, color_yellow, image_font_stroke )
                        cv2.rectangle( image, (x_pos+5, y_pos+5), (x_pos+width-5, y_pos+height-5), color_yellow, stroke_width )
                        self.yellow_light = True

        return value



# Starting thread server handler
if __name__ == '__main__':
    ThreadServer()
