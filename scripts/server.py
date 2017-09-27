# Import libraries
import threading
import socketserver
import socket
import cv2
import numpy as np
import math

# Config vars
server_ip = '192.168.1.235'
server_port = 8000
image_fps = 24 
image_width = 320
image_height = 240

color_red = (211, 47, 47)
color_yellow = (255, 238, 88)
color_blue = (48, 79, 254)
color_green = (0, 168, 0)

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


# Class to handle the jpeg video stream received from client
class VideoStreamHandler(socketserver.StreamRequestHandler):
  
    def handle(self):
 
        stream_bytes = b' '

        # stream video frames one by one
        try:
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
                    half_gray = gray[120:240, :]

                    # Dibujamos lineas "control"
                    if stroke_enabled:
                        for stroke in stroke_lines:
                            cv2.line( image, stroke[0], stroke[1], stroke[2], stroke[3])

                    # Mostramos imagenes
                    cv2.imshow('image', image)
                    cv2.imshow('mlp_image', half_gray)

                    # reshape image
                    image_array = half_gray.reshape(1, 38400).astype(np.float32)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            cv2.destroyAllWindows()

        finally:
            print( 'Connection closed on videostream thread' )

# Class to handle the different threads 
class ThreadServer():

    # Server thread to handle the video
    def server_thread(host, port):
        server = socketserver.TCPServer((host, port), VideoStreamHandler)
        server.serve_forever()

    print( '+ Starting videostream server in ' + str( server_ip ) + ':' + str( server_port ) )
    video_thread = threading.Thread(target=server_thread( server_ip, server_port))
    video_thread.start()

# Starting thread server handler
if __name__ == '__main__':
    ThreadServer( server_ip, server_port )
