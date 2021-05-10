import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(40, GPIO.OUT, initial=GPIO.LOW) # Set pin 40 to be an output pin and set initial value to low (off)
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)

def on():
    GPIO.output(40, GPIO.HIGH) # Turn on
    
def off():
    GPIO.output(40, GPIO.LOW) # Turn off

def blink():
    while True:
        GPIO.output(40, GPIO.LOW)
        sleep(0.5)
        GPIO.output(40, GPIO.HIGH)
        sleep(0.5)
        
def buzzer():
    while True:
        GPIO.output(18, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(18, GPIO.LOW)
        sleep(0.5)
# buzzer()