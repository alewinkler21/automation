import RPi.GPIO as GPIO
import logger as logger

colors = {'red':0xFF0000, 
          'green':0x00FF00, 
          'blue':0x0000FF, 
          'yellow':0xFFFF00, 
          'magenta':0xFF00FF, 
          'aqua':0x00FFFF}

pins = {'pin_R':17, 
        'pin_G':27, 
        'pin_B':22}

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for i in pins:
    GPIO.setup(pins[i], GPIO.OUT)
    GPIO.output(pins[i], GPIO.HIGH)
# set Frequece
p_R = GPIO.PWM(pins['pin_R'], 2000)  
p_G = GPIO.PWM(pins['pin_G'], 2000)
p_B = GPIO.PWM(pins['pin_B'], 5000)
# initial duty Cycle = 0(leds off)
p_R.start(0)      
p_G.start(0)
p_B.start(0)
    

def mapColor(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(color):
    if not color in colors:
        logger.error("color doesn't exist")
        return
    
    col = colors[color]
    
    R_val = (col & 0x110000) >> 16
    G_val = (col & 0x001100) >> 8
    B_val = (col & 0x000011) >> 0
    
    R_val = mapColor(R_val, 0, 255, 0, 100)
    G_val = mapColor(G_val, 0, 255, 0, 100)
    B_val = mapColor(B_val, 0, 255, 0, 100)
    # change duty cycle
    p_R.ChangeDutyCycle(R_val)     
    p_G.ChangeDutyCycle(G_val)
    p_B.ChangeDutyCycle(B_val)

def dispose():
    p_R.stop()
    p_G.stop()
    p_B.stop()
    # turn off all leds
    for p in pins:
        GPIO.output(pins[p], GPIO.HIGH)    
    GPIO.cleanup()
