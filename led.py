import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
try:
    GPIO.output(8, GPIO.HIGH)
    print('output is high')
    GPIO.output(8, GPIO.LOW)
    print('output is low')
except:
    GPIO.cleanup()