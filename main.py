import numpy as np
import cv2

img = cv2.imread('./image.png', cv2.IMREAD_COLOR)

hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

lower = np.array([40, 70, 70])
upper = np.array([70, 255, 255])

# Threshold to only get the color we want
mask = cv2.inRange(hsv, lower, upper)

# Bitwise-AND mask and original
res = cv2.bitwise_and(img, img, mask = mask)

cv2.imshow('image',img)
cv2.imshow('mask', mask)
cv2.imshow('res', res)

cv2.waitKey(0)
cv2.destroyAllWindows()