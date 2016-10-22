import cv2
import numpy as np
from scipy.signal import argrelextrema
from matplotlib import pyplot as plt


# Image to Intensity
# Given an image, returns a numpy type array containing
# number of pixels at intensities 0 - 255.
def img_to_intensity(input_img):
    '''
    :param img: Image to be processed.
    :return: numpy type array of pixel intensities.
    '''
    # Convert image to gray scale and copy into variable.
    gray_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    # Calculate intensity histogram.
    hist_int = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    # Convert histogram to numpy array.
    return np.array(hist_int)


def global_local_extrema(arr):
    '''
    :param arr:
    :return: 
    '''
    # Calculate min and max of numpy array.
    max_global = np.max(arr)
    min_global = np.min(arr)
    max_local = argrelextrema(arr, np.greater, order=50)
    min_local = argrelextrema(arr, np.less, order=50)
    return np.array([max_global] + max_local[0]), \
           np.array([min_global] + min_local[0])


# Import image into program.
img = cv2.imread('beach.jpg')

img_arr = img_to_intensity(img)
print global_local_extrema(img_arr)
