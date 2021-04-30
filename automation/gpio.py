import RPi.GPIO as GPIO
import time
from automation import logger

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def toggle(status, pin):
    GPIO.setup(pin, GPIO.OUT)
    if status:
#         print ("status: {0}, pinNumber: {1}".format("status", pin))
        GPIO.output(pin, GPIO.HIGH)
    else:
#         print( "status: {0}, pinNumber: {1}".format("off", pin))
        GPIO.output(pin, GPIO.LOW)

def configurePinAsInput(pin):
    # set the pin as output and value to off 
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)
    # change the pin back to input
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def initButton(button, fn):
    configurePinAsInput(button.pin)
    # subscribe to rising event
    GPIO.add_event_detect(button.pin, GPIO.RISING, callback=lambda x: fn(button), bouncetime=500)

def initSensor(sensor):
    configurePinAsInput(sensor.pin)
    
def readSensorValue(sensor):
#     return False
    return GPIO.input(sensor.pin) == GPIO.HIGH

def timeToHigh(sensor):
    configurePinAsInput(sensor.pin)
    # count until the pin goes high or timeout
    count = 0
    sensorTimeOut = 10
    timedOut = False
    ts = time.time()
    while (not readSensorValue(sensor) and not timedOut):
        count += 1
        timedOut = (time.time() - ts) >= sensorTimeOut
        time.sleep(0.1)
    if timedOut:
        logger.warning("Sensor timed out. Count is " + str(count))
    return count

def cleanUp():
#     pass
    GPIO.cleanup()
