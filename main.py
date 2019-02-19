#!/usr/bin/python3

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

# Servo
servoPIN = 18
GPIO.setwarnings(False) # Do not tell anyone
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
servo = GPIO.PWM(servoPIN, 50)
servo.start(0.1) # "Neutral"
time.sleep(0.1)
servo.ChangeDutyCycle(0)

# Camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 6
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(1) # Camera needs some time for itself

# Image transformation
lower = np.array([30, 70, 70])
upper = np.array([70, 255, 255])


for rgbFrame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):
        print("Quit")
        break
    
    hsvFrame = cv2.cvtColor(rgbFrame.array, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsvFrame, lower, upper)
    nonZeroPixels = cv2.countNonZero(mask)
    
    '''
    cv2.putText(mask, "%s" %(nonZeroPixels), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
    cv2.imshow("mask", mask)
    '''

    rawCapture.truncate(0)
    
    if nonZeroPixels > 10000:
        # Turn servo on
        servo.ChangeDutyCycle(0.1)
        time.sleep(0.1)
        # Activate the button
        servo.ChangeDutyCycle(3.5)
        time.sleep(0.4)
        # Go back to the off position
        servo.ChangeDutyCycle(0.1)
        time.sleep(0.1)
        # Turn servo off
        servo.ChangeDutyCycle(0)
        # Sleep so we do not keep hitting the button
        time.sleep(3)

p.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
