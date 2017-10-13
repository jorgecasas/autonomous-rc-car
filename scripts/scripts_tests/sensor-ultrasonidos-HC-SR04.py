# Importamos librerias RPi.GPIO (entradas/salidas GPIO de Raspberry Pi) y time (para sleeps, etc...)
# Reqiuere previamente instalarla (pip install RPi.GPIO)
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM) #Ponemos la placa en modo BCM

# Definimos los pines GPIO de la Raspberry Pi 3 (segun esquema)
#   12 - Led (output)
#   18 - Trigger (output)
#   24 - Echo (input)
GPIO_LED = 12
GPIO_TRIGGER = 18
GPIO_ECHO = 24

# Configuramos los pines como salidas (trigger y led) o entradas (detector de eco)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT) #Configuramos Trigger como salida
GPIO.setup(GPIO_ECHO,GPIO.IN) #Configuramos Echo como entrada
GPIO.setup( GPIO_LED, GPIO.OUT ) # Pin de led

# Inicializamos los pines de salida (apagados)
GPIO.output( GPIO_TRIGGER, False ) 
GPIO.output( GPIO_LED, False )

# Distancia en cm
distance_limit = 15

try:
    print( 'Sensor ultrasonico HC-SR04' )

    # Iniciamos un loop infinito
    while True: 

        # Enviamos un pulso de ultrasonidos durante un poco de tiempo
        GPIO.output(GPIO_TRIGGER,True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER,False)
        
        # Desde que dejamos de enviar el pulso, obtenemos tiempo actual
        start = time.time()

        # Si el sensor no recibe sonido, mantenemos el tipo actual actualizado
        while GPIO.input(GPIO_ECHO)==0:
            start = time.time()

        # Si el sensor recibe sonido, obtenemos el tiempo fin
        while GPIO.input(GPIO_ECHO)==1:
            stop = time.time()

        # Obtenemos el tiempo transcurrido. 
        # La distancia sera igual al tiempo transcurrido por la velocidad (partido por 2, porque 
        # el sonido va y vuelve desde el sensor al objeto y del objeto al sensor): 2 D = (T x V)/2
        elapsed = stop-start
        distance = (elapsed * 34300) / 2
        
        # Si la distancia es menor que la distancia limite fijada... Paramos y encendemos led de alerta!
        if distance < distance_limit:
            print( 'Stop! Objeto a ' + str( distance ) +'cm' )
            GPIO.output( GPIO_LED, True )
        else:
            # En este caso, podemos continuar avanzando sin obstaculos!
            print( 'Go! No hay objetos delante' )
            GPIO.output( GPIO_LED, False )

        # Pausamos un poco para no saturar el procesador de la Raspberry Pi
        time.sleep( 0.25 )

except KeyboardInterrupt: 
    # Si el usuario pulsa CONTROL+C... fin de aplicacion (limpieando los pines GPIO)
    print( 'Sensor Stopped' )
    GPIO.cleanup()
