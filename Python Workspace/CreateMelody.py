import cv2
import random
import numpy as np
from scipy.signal import argrelextrema
from melopy import *
# Speed of sound in meters per second.
SOUND = 343.2


# Image to Intensity
# Given an image, returns a NumPy type array containing
# number of pixels at intensities 0 - 255.
def img_to_intensity(input_img):
    """
    :param input_img: Image to be processed.
    :return: NumPy type array of pixel intensities.
    """
    # Convert image to gray scale and copy into variable.
    gray_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
    # Calculate intensity histogram.
    hist_int = cv2.calcHist([gray_img], [0], None, [256], [0, 256])
    # Convert histogram to NumPy array.
    return np.array(hist_int)


# Global and Local Extrema
# Given a NumPy type array, return the indices of all minimum
# and maximum that occur (within a threshold order).
def global_local_extrema(arr):
    """
    :param arr: NumPy type array.
    :return: NumPy type array of indices of local and
    global extrema of arr.
    """
    # Calculate global min and max of arr.
    max_global = np.argmax(arr)
    min_global = np.argmin(arr)
    # Calculate local min and max of arr.
    max_local = argrelextrema(arr, np.greater, order=5)
    min_local = argrelextrema(arr, np.less, order=5)
    # Return two separate arrays.
    return np.append(max_local[0], max_global), \
        np.append(min_local[0], min_global)


# Given a scale, calculate and return the notes in that scale as
# well as the corresponding wavelengths.
def scale_to_wavelengths(scale, major):
    """
    :param scale: String of scale to be calculated.
    :return: Two NumPy type arrays. One containing string values of
    notes and the other of the corresponding frequencies.
    """
    if major:
        return major_scale(scale), \
            [(1 / x) * SOUND for x in map(note_to_frequency, major_scale(scale))]
    else:
        return minor_scale(scale), \
               [(1 / x) * SOUND for x in map(note_to_frequency, minor_scale(scale))]


# Map to Wavelength
# Given two points on the range 0-255, map the distance
# between the points and match to the closest wavelength
# in the NOTES_LIST array declared previously.
def map_to_wavelength(point1, point2, scale_wavelength):
    """
    :param point1: Point value corresponding to range 0-255.
    :param point2: Point value corresponding to range 0-255.
    :param scale_wavelength: Array of wavelengths corresponding
    to notes in a scale.
    :return: Index of closest wavelength mapped to distance.
    """
    # Calculate distance between points on 0-255 range.
    dist = abs(point1 - point2)
    # Map to range of wavelengths in passed array.
    max_wavelength = max(scale_wavelength)
    min_wavelength = min(scale_wavelength)
    mapped_dist = dist * ((max_wavelength - min_wavelength) / 255) + min_wavelength

    # Calculate closest wavelength and return.
    return (np.abs(scale_wavelength - mapped_dist)).argmin()


# Average Color
# Given an image (or a portion of an image) obtain the average color.
def average_color(input_img):
    """
    :param input_img: Image or section of image to be processed.
    :return: Hexadecimal version of RGB value of average color.
    """
    # Take average of all rows and average those for image average.
    average_color_per_row = np.average(input_img, axis=0)
    average_img_color = np.average(average_color_per_row, axis=0)
    # Return hexadecimal form of average color.
    return (int(average_img_color[0]) << 16) + \
        (int(average_img_color[1]) << 8) + \
        int(average_img_color[2])


# Main
# Construct the melody creating a unique set of notes (and length) for each
# region of the image.
def main(scale, major, tempo):
    """
    :param scale: String representation of scale (i.e 'C4').
    :param major: Boolean if in major key.
    :param tempo: Integer to define tempo (speed) of music.
    :return: None. Export .wav file of generated music.
    """
    img = cv2.imread('beach.jpg')

    # Store height and width of image.
    height, width = len(img), len(img[0])
    # Calculate dimensions of sub-image regions (2x2 grid).
    region_height, region_width = height / 4, width / 4

    # Calculate wavelength range and notes in working scale.
    scale_notes, scale_notes_wavelengths = scale_to_wavelengths(scale, major)

    # Array to hold notes played (not used now, but in future,
    # possibly with piping to JavaScript Tone.js).
    notes = []
    # Initiate needed variables for main loop.
    melody = Melopy('test_song', tempo=tempo)
    x, y = 0, 0

    for j in xrange(5):  # Some case, we can change this to anything to make infinite.
        # Iterate through all regions of image.
        while x < width:
            while y < height:
                # Obtain current region to be processed.
                img_region = img[y: y + region_height, x: x + region_width]
                # Create intensity histogram of image section.
                int_hist = img_to_intensity(img_region)
                # Calculate extrema of histogram.
                max_arr, min_arr = global_local_extrema(int_hist)

                # Calculate average color and seed random with color.
                average_color_region = average_color(img_region)
                random.seed(average_color_region)

                # Obtain note corresponding to region wavelength.
                region_note = scale_notes[map_to_wavelength(max_arr[random.randint(0, len(max_arr) - 1)],
                                                            min_arr[random.randint(0, len(min_arr) - 1)],
                                                            scale_notes_wavelengths)]

                # Generate triad for current note with random number of notes included.
                if major:
                    region_triad = major_triad(region_note)[0:random.randint(1, 3)]
                else:
                    region_triad = minor_triad(region_note)[0:random.randint(1, 3)]

                # Add note with random length.
                notes.append(region_triad)
                melody.add_fractional_note(region_triad, 1.0)

                y += region_height  # Necessary for loop.
            y = 0  # Necessary for loop.
            x += region_width  # Necessary for loop.
        x = 0  # Necessary for loop.

    # Render the melody and export .wav file for playback.
    melody.render()
    print notes

if __name__ == "__main__":
    main('C4', True, 140)

