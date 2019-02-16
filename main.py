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
servo.start(7.5) # "Neutral"
servo.ChangeDutyCycle(5.0)

# Camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 12
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(1) # Camera needs some time for itself

# Image transformation
lower = np.array([30, 70, 70])
upper = np.array([70, 255, 255])


for rgbFrame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):
        print("Quit")
        break
    
    hsvFrame = cv2.cvtColor(rgbFrame, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsvFrame, lower, upper)
    nonZeroPixels = cv2.countNonZero(mask)
    
    cv2.imshow("mask", mask)


p.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
