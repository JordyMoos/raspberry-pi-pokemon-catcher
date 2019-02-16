import RPi.GPIO as GPIO
import time

servoPIN = 18

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

pwm = GPIO.PWM(servoPIN, 50)
pwm.start(7.5)
time.sleep(1)

try:
  while True:
   pwm.ChangeDutyCycle(10.0)
   time.sleep(0.2)
   pwm.ChangeDutyCycle(7.5)
   time.sleep(3)
   
except KeyboardInterrupt:
    pass




p.stop()
GPIO.cleanup()