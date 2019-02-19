#!/usr/bin/python3

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

# Config
minimumPixels = 10000

# GPIO Setup
GPIO.setwarnings(False) # Do not tell anyone
GPIO.setmode(GPIO.BCM)

# Pokeball Servo
pokeballServoPin = 18
GPIO.setup(pokeballServoPin, GPIO.OUT)
pokeballServo = GPIO.PWM(pokeballServoPin, 50)
pokeballServo.start(0.1) # "Neutral"
time.sleep(0.1)
pokeballServo.ChangeDutyCycle(0)

# Pair button
pairPIN = 27
GPIO.setup(pairPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Pair Servo
pairServoPin = 17
GPIO.setup(pairServoPin, GPIO.OUT)
pairServo = GPIO.PWM(pairServoPin, 50)
pairServo.start(0.1) # "Neutral"
time.sleep(0.1)
pairServo.ChangeDutyCycle(0)

# Camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 6
camera.hflip = True
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(1) # Camera needs some time for itself

# Image transformation
blueLower = np.array([100, 70, 70])
blueUpper = np.array([125, 255, 255])
greenLower = np.array([30, 70, 70])
greenUpper = np.array([70, 255, 255])

for rgbFrame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        print("Quit")
        break
    
    hsvFrame = cv2.cvtColor(rgbFrame.array, cv2.COLOR_RGB2HSV)
    
    # Pokestop
    blueMask = cv2.inRange(hsvFrame, blueLower, blueUpper)
    blueCount = cv2.countNonZero(blueMask)
    
    # Pokemon
    greenMask = cv2.inRange(hsvFrame, greenLower, greenUpper)
    greenCount = cv2.countNonZero(greenMask)
    
    '''
    cv2.putText(mask, "%s" %(nonZeroPixels), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
    cv2.imshow("mask", mask)
    '''

    rawCapture.truncate(0)
    
    if GPIO.input(pairPIN) == False:
        print("Button Pressed")
        time.sleep(0.2)
    
    elif blueCount > minimumPixels and blueCount > greenCount:
        print("Pokestop Blue={} Green=".format(blueCount, greenCount))
        time.sleep(2)
    
    elif greenCount > minimumPixels:
        print("Pokemon {}".format(greenCount))
        # Turn servo on
        pokeballServo.ChangeDutyCycle(0.1)
        time.sleep(0.1)
        # Activate the button
        pokeballServo.ChangeDutyCycle(3.5)
        time.sleep(0.4)
        # Go back to the off position
        pokeballServo.ChangeDutyCycle(0.1)
        time.sleep(0.1)
        # Turn servo off
        pokeballServo.ChangeDutyCycle(0)
        # Sleep so we do not keep hitting the button
        time.sleep(3)

pokeballServoPin.stop()
pairServo.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
