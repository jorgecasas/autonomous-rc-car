# Controlling two DC motors with Raspberry Pi and servo controller bridge L298N
import RPi.GPIO as GPIO 
import time
import curses

print( '+ Starting servo control using keyboard' )
print( '+ Use directional keys to steer right and left (or "s" to continue steering straight), accelerate forward and backwards, and Space to brake! Press "q" to quit.' )
time.sleep(1.5) 

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
MOTOR_01_GPIO_FORWARD = 20
MOTOR_01_GPIO_BACKWARD = 21

# GPIO pins configuration for DC Motor 2 
MOTOR_02_GPIO_RIGHT = 27
MOTOR_02_GPIO_LEFT = 17

# Enabling GPIO configured pins as OUTPUT - Also, create objects PWM on ports defined with 50 Hertz configuration
GPIO.setup( MOTOR_01_GPIO_FORWARD, GPIO.OUT)
GPIO.setup( MOTOR_01_GPIO_BACKWARD, GPIO.OUT)

GPIO.setup( MOTOR_02_GPIO_RIGHT, GPIO.OUT)
GPIO.setup( MOTOR_02_GPIO_LEFT, GPIO.OUT)


# Class for servo controlling
class ServoController(object):

    # Last key pressed
    LastKey = ""

    def Stop(self):
        GPIO.output( MOTOR_01_GPIO_FORWARD, GPIO.LOW)
        GPIO.output( MOTOR_01_GPIO_BACKWARD, GPIO.LOW)
        GPIO.output( MOTOR_02_GPIO_LEFT, GPIO.LOW)
        GPIO.output( MOTOR_02_GPIO_RIGHT, GPIO.LOW)
        print( '=== Stop (brake) \r' )

    def Straight(self):
        GPIO.output( MOTOR_02_GPIO_LEFT, GPIO.LOW)
        GPIO.output( MOTOR_02_GPIO_RIGHT, GPIO.LOW)
        print('| | Continue straight \r')


    def Left(self):
        if LastKey != 'left' : Straight()
        GPIO.output( MOTOR_02_GPIO_RIGHT, GPIO.LOW)
        GPIO.output( MOTOR_02_GPIO_LEFT, GPIO.HIGH)
        print('\ \ Steer left \r')

    def Right(self):
        if LastKey != 'right' : Straight()
        GPIO.output( MOTOR_02_GPIO_LEFT, GPIO.LOW)
        GPIO.output( MOTOR_02_GPIO_RIGHT, GPIO.HIGH)
        print('/ / Steer right \r')

    def Forward(self):
        GPIO.output( MOTOR_01_GPIO_BACKWARD, GPIO.LOW)
        GPIO.output( MOTOR_01_GPIO_FORWARD, GPIO.HIGH)
        print('+++ Accelerate forward \r')

    def Backward(self): 
        GPIO.output( MOTOR_01_GPIO_FORWARD, GPIO.LOW)
        GPIO.output( MOTOR_01_GPIO_BACKWARD, GPIO.HIGH)
        print('--- Accelerate backwards \r')

try:
    servo_controller = ServoController()

    while True:
        char = screen.getch()
        if char == ord('q'):
            # Ending
            break

        elif char == ord(' '):
            LastKey="enter"
            servo_controller.Stop()

        elif char == ord('s'):
            LastKey="enter"
            servo_controller.Straight()

        elif char == curses.KEY_RIGHT:
            LastKey="right"
            servo_controller.Right() 
           
        elif char == curses.KEY_LEFT:
            LastKey="left"
            servo_controller.Left()

        elif char == curses.KEY_UP:
            LastKey="up"
            servo_controller.Forward()

        elif char == curses.KEY_DOWN:
            LastKey="down"
            servo_controller.Backward()

finally:
    # Shut down cleanly and clean GPIO output pins
    curses.nocbreak(); 
    screen.keypad( 0 ); 
    curses.echo()
    curses.endwin()

    # Stop GPIO and cleaning pins
    GPIO.output( MOTOR_01_GPIO_FORWARD, GPIO.LOW)
    GPIO.output( MOTOR_01_GPIO_BACKWARD, GPIO.LOW)
    GPIO.output( MOTOR_02_GPIO_LEFT, GPIO.LOW)
    GPIO.output( MOTOR_02_GPIO_RIGHT, GPIO.LOW)
    GPIO.cleanup()

    print ('Ending servo controller')
