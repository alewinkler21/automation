import RPi.GPIO as GPIO
import time
import logger

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def toggleGPIO(status, pin):
    GPIO.setup(pin, GPIO.OUT)
    if status:
        #print ("status: {0}, pinNumber: {1}".format("status", pin))
        GPIO.output(pin, GPIO.HIGH)
    else:
        #print( "status: {0}, pinNumber: {1}".format("off", pin))
        GPIO.output(pin, GPIO.LOW)

def initButton(button, fn):
    # set the pin as output and value to off 
    GPIO.setup(button.pin, GPIO.OUT)
    GPIO.output(button.pin, GPIO.LOW)
    time.sleep(0.1)
    # change the pin back to input
    GPIO.setup(button.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    # subscribe to rising event
    GPIO.add_event_detect(button.pin, GPIO.RISING, callback=lambda x: fn(button), bouncetime=500)

def timeToHigh(pin):
    # output on the pin for 
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)
    # change the pin back to input
    GPIO.setup(pin, GPIO.IN)
    # count until the pin goes high or timeout
    count = 0
    sensorTimeOut = 10
    timedOut = False
    ts = time.time()
    while (GPIO.input(pin) == GPIO.LOW and not timedOut):
        count += 1
        timedOut = (time.time() - ts) >= sensorTimeOut
        time.sleep(0.1)
    if timedOut:
        logger.warning("Sensor timed out. Count is " + str(count))
    return count

def cleanUp():
    GPIO.cleanup()
