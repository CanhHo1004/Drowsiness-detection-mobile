import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
from time import sleep # Import the sleep function from the time module
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(40, GPIO.OUT, initial=GPIO.LOW) # Set pin 40 to be an output pin and set initial value to low (off)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def on():
    GPIO.output(40, GPIO.HIGH) # Turn on
    
def off():
    GPIO.output(40, GPIO.LOW) # Turn off
    
def blink(state):
    while True:
        on()
        sleep(0.3)
        off()
        sleep(0.6)
        if state == 1:
            break
    
def button():
    while True:
        button_state = GPIO.input(37)
        if button_state == False:
            on()
            