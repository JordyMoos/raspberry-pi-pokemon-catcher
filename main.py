#!/usr/bin/python3

from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

# Config
PIN_PAIR = 27
PIN_SERVO_PAIR = 12
PIN_SERVO_POKEBALL = 18
REPAIR_IDLE_TIME = 60 * 7
REPAIR_DELAY_TIME = 30

MINIMUM_PIXELS = 10000
RESOLUTION = (640, 480)


def setup_servo(pin):
    GPIO.setup(pin, GPIO.OUT)
    servo = GPIO.PWM(pin, 50)
    servo.start(0.1)
    time.sleep(0.2)
    servo.ChangeDutyCycle(0)
    return servo


def trigger_servo(servo):
    # Turn servo on
    servo.ChangeDutyCycle(0.1)
    time.sleep(0.1)
    # Activate the button
    servo.ChangeDutyCycle(3.5)
    time.sleep(0.2)
    # Go back to the off position
    servo.ChangeDutyCycle(0.1)
    time.sleep(0.1)
    # Turn servo off
    servo.ChangeDutyCycle(0)


# GPIO Setup
GPIO.setwarnings(False)  # Do not tell anyone
GPIO.setmode(GPIO.BCM)

# Servo's
pairServo = setup_servo(PIN_SERVO_PAIR)
pokeballServo = setup_servo(PIN_SERVO_POKEBALL)

# Pair button
GPIO.setup(PIN_PAIR, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Camera
camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = 6
rawCapture = PiRGBArray(camera, size=RESOLUTION)
time.sleep(1)  # Camera needs some time for itself

# Image transformation
blueLower = np.array([10, 70, 70])
blueUpper = np.array([30, 255, 255])
greenLower = np.array([35, 70, 70])
greenUpper = np.array([70, 255, 255])

lastInteraction = time.time() - 1000000

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

    # res = cv2.bitwise_and(rgbFrame.array, rgbFrame.array, mask = blueMask)
    # cv2.imshow('rgbFrame', rgbFrame.array)
    # cv2.imshow('blueMask', blueMask)
    # cv2.imshow('greenMask', greenMask)
    # cv2.imshow('res', res)

    rawCapture.truncate(0)

    if not GPIO.input(PIN_PAIR):
        print("Button Pressed")
        trigger_servo(pairServo)
        trigger_servo(pokeballServo)
        time.sleep(1)

    elif blueCount > MINIMUM_PIXELS and blueCount > greenCount:
        lastInteraction = time.time()
        time.sleep(2)

    elif greenCount > MINIMUM_PIXELS:
        lastInteraction = time.time()
        trigger_servo(pokeballServo)
        # Sleep so we do not keep hitting the button
        time.sleep(3)

    elif lastInteraction < time.time() - REPAIR_IDLE_TIME:
        trigger_servo(pairServo)
        trigger_servo(pokeballServo)
        lastInteraction = time.time() - REPAIR_IDLE_TIME - REPAIR_DELAY_TIME
        time.sleep(5)

pokeballServo.stop()
pairServo.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
