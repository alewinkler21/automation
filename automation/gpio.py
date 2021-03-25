#import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

def toggleGPIO(status, pin):
    #GPIO.setup(pin, GPIO.OUT)
    if status:
        print ("status: {0}, pinNumber: {1}".format("status", pin))
        #GPIO.output(pin, GPIO.HIGH)
    else:
        print( "status: {0}, pinNumber: {1}".format("off", pin))
        #GPIO.output(pin, GPIO.LOW)