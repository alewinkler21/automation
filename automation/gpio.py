#import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

def toggle_gpio(on, pin):
    #GPIO.setup(pin, GPIO.OUT)
    if on:
        print ("status: {0}, pinNumber: {1}".format("on", pin))
        #GPIO.output(pin, GPIO.HIGH)
    else:
        print( "status: {0}, pinNumber: {1}".format("off", pin))
        #GPIO.output(pin, GPIO.LOW)