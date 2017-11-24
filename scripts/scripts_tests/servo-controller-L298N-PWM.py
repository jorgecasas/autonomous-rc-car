# Controlling two DC motors with Raspberry Pi and servo controller bridge L298N
import RPi.GPIO as GPIO 
import time
import curses


# Initializing curses to get keyboard strokes
screen = curses.initscr()
 
# Turn off input echoing and set response to keys immediately (no ENTER key required)
# Also, map arrow keys (keypad) to special values - Keyboard symbols: https://docs.python.org/2/library/curses.html
curses.noecho()
curses.cbreak()
screen.keypad( True )

# Raspberry Pi and L298N bridge must have the same GROUND pins interconnected
# Choose BCM numbering schemes for GPIO pins in Raspberry Pi  
GPIO.setmode(GPIO.BCM)  

# GPIO pins configuration for DC Motor 1
MOTOR_01_GPIO_ENABLER = 18
MOTOR_01_GPIO_OUTPUT_01 = 23
MOTOR_01_GPIO_OUTPUT_02 = 24

# GPIO pins configuration for DC Motor 2
MOTOR_02_GPIO_ENABLER = 13
MOTOR_02_GPIO_OUTPUT_01 = 27
MOTOR_02_GPIO_OUTPUT_02 = 17

# Enabling GPIO configured pins as OUTPUT - Also, create objects PWM on ports defined with 50 Hertz configuration
# PWM for DC Motor 1
GPIO.setup( MOTOR_01_GPIO_ENABLER, GPIO.OUT)
GPIO.setup( MOTOR_01_GPIO_OUTPUT_01, GPIO.OUT)
GPIO.setup( MOTOR_01_GPIO_OUTPUT_02, GPIO.OUT)

MOTOR_01_PWM_ENABLER = GPIO.PWM( MOTOR_01_GPIO_ENABLER, 100)
MOTOR_01_PWM_OUTPUT_01 = GPIO.PWM( MOTOR_01_GPIO_OUTPUT_01, 100)
MOTOR_01_PWM_OUTPUT_02 = GPIO.PWM( MOTOR_01_GPIO_OUTPUT_02, 100)

# PWM for DC Motor 2
GPIO.setup( MOTOR_02_GPIO_ENABLER, GPIO.OUT)
GPIO.setup( MOTOR_02_GPIO_OUTPUT_01, GPIO.OUT)
GPIO.setup( MOTOR_02_GPIO_OUTPUT_02, GPIO.OUT)

MOTOR_02_PWM_ENABLER = GPIO.PWM( MOTOR_02_GPIO_ENABLER, 100)
MOTOR_02_PWM_OUTPUT_01 = GPIO.PWM( MOTOR_02_GPIO_OUTPUT_01, 100)
MOTOR_02_PWM_OUTPUT_02 = GPIO.PWM( MOTOR_02_GPIO_OUTPUT_02, 100)

# Variables for outputs PWM
PWM_OFF = 0
PWM_MEDIUM = 60
PWM_FULL = 100

# Class for servo controlling
class ServoController(object):

    # Last key pressed
    LastKey = ""

    def Stop():
        MOTOR_01_PWM_OUTPUT_02.start( PWM_OFF )
        MOTOR_01_PWM_OUTPUT_01.start( PWM_OFF )
        MOTOR_01_PWM_ENABLER.start( PWM_OFF )

        MOTOR_02_PWM_OUTPUT_02.start( PWM_OFF )
        MOTOR_02_PWM_ENABLER.start( PWM_OFF )
        MOTOR_02_PWM_OUTPUT_01.start( PWM_OFF )
        time.sleep(0.3) 
        print ("Stop executed") 

    def Left():
        if LastKey != 'left' : Stop()
        MOTOR_01_PWM_ENABLER.start( PWM_FULL )
        MOTOR_01_PWM_OUTPUT_01.start( PWM_OFF )
        MOTOR_01_PWM_OUTPUT_02.start( PWM_MEDIUM )

        time.sleep(0.4)
        MOTOR_02_PWM_ENABLER.start( PWM_OFF )
        MOTOR_02_PWM_OUTPUT_01.start( PWM_FULL )
        MOTOR_02_PWM_OUTPUT_02.start( PWM_MEDIUM )
     

    def Right():
        if LastKey != 'right' : Stop()
        MOTOR_01_PWM_ENABLER.start( PWM_OFF )
        MOTOR_01_PWM_OUTPUT_01.start( PWM_FULL )
        MOTOR_01_PWM_OUTPUT_02.start( PWM_MEDIUM )

        time.sleep(0.4)
        MOTOR_02_PWM_ENABLER.start( PWM_FULL )
        MOTOR_02_PWM_OUTPUT_01.start( PWM_OFF )
        MOTOR_02_PWM_OUTPUT_02.start( PWM_MEDIUM )
     

    def Up(): 
        MOTOR_01_PWM_ENABLER.start( PWM_OFF )
        MOTOR_01_PWM_OUTPUT_01.start( PWM_FULL )
        MOTOR_01_PWM_OUTPUT_02.start( PWM_MEDIUM )

        time.sleep(0.3)
        MOTOR_02_PWM_ENABLER.start( PWM_OFF )
        MOTOR_02_PWM_OUTPUT_01.start( PWM_FULL )
        MOTOR_02_PWM_OUTPUT_02.start( PWM_MEDIUM )

        time.sleep(0.3) 

    def Down(): 
        MOTOR_01_PWM_ENABLER.start( PWM_FULL )
        MOTOR_01_PWM_OUTPUT_01.start(0)
        MOTOR_01_PWM_OUTPUT_02.start(60)

        time.sleep(0.3)
        MOTOR_02_PWM_ENABLER.start( PWM_FULL )
        MOTOR_02_PWM_OUTPUT_01.start(0)
        MOTOR_02_PWM_OUTPUT_02.start(60)

        time.sleep(0.3)

try:
    servo_controller = ServoController()

    while True:
        char = screen.getch()
        if char == ord('q'):
            # Ending
            break

        elif char == ord(' '):
            LastKey="enter"
            print ('Stop === \n')
            servo_controller.Stop()

        elif char == curses.KEY_RIGHT:
            LastKey="right"
            print ('Right >>> \n')
            servo_controller.Right() 
           
        elif char == curses.KEY_LEFT:
            LastKey="left"
            print ('Left <<< \n')
            servo_controller.Left()

        elif char == curses.KEY_UP:
            LastKey="up"
            print ('Accelerate +++ \n')
            servo_controller.Up()

        elif char == curses.KEY_DOWN:
            LastKey="down"
            print ('Brake --- \n')
            servo_controller.Down()

finally:
    # Shut down cleanly and clean GPIO output pins
    print ('Ending servo controller')
    curses.nocbreak(); 
    screen.keypad( 0 ); 
    curses.echo()
    curses.endwin()

    # Stop PWM output
    MOTOR_01_PWM_ENABLER.stop()
    MOTOR_01_PWM_OUTPUT_01.stop()
    MOTOR_01_PWM_OUTPUT_02.stop()

    MOTOR_02_PWM_ENABLER.stop()
    MOTOR_02_PWM_OUTPUT_01.stop()
    MOTOR_02_PWM_OUTPUT_02.stop()

    GPIO.cleanup()
