# ---------- Libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ------------------- Implimentation With Test Image:
# ------- Importing image
image = cv2.imread("Photos/LC08_L1TP_051012_20200810_20200810_01_RT.jpg")
image =cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

# -------- Img properties

# Corners of the sat image
from pyproj import Proj
UL_lat = 69.41141
UL_long = -119.06171
LR_lat = 67.08418
LR_long = -113.01863
# Converting to UTM

# ------------ Get Area

def get_area(UL_lat, UL_long, LR_lat, LR_long):
    myProj = Proj("+proj=utm +zone=23K, +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    UL_UTMx, UL_UTMy = myProj(UL_long, UL_lat)
    LR_UTMx, LR_UTMy = myProj(LR_long, LR_lat)

    total_area = (UL_UTMx - LR_UTMx) * (UL_UTMy - LR_UTMy)
    return total_area

# ------------ Cropping
y1 = 5400
y2 = 5700
x1 = 2500
x2 = 2800

image_cropped = image[y1:y2, x1:x2]
#plt.imshow(image_cropped)
# ------- K Mean


def kmeans(img, K, attempts=30, show=True):
    vectorized = img.reshape((-1,3))
    vectorized = np.float32(vectorized)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(vectorized, K, None, criteria, attempts, cv2.KMEANS_PP_CENTERS)
    center = np.uint8(center)
    res = center[label.flatten()]
    # Output the result image
    result_image = res.reshape(img.shape)
    if show:
        plt.imshow(result_image)
    return result_image

# ----- Pixel Scan
# From StackOverflow: https://stackoverflow.com/questions/24780697/numpy-unique-list-of-colors-in-the-image
def get_dark_array(img):
    uniquepixel = np.unique(img.reshape(-1, img.shape[2]), axis=0)
    blue_max = 255
    dark_array = []
    for pixel in uniquepixel:
        blue = pixel[0]
        if blue < blue_max:
            dark_array = np.array(pixel)
            blue_max = blue

    return dark_array


# Implimentation
result_image = kmeans(image_cropped, 2, show=False)
plt.imshow(image)
plt.imshow(image_cropped)
plt.imshow(result_image)
dark_array = get_dark_array(result_image)

# Auto cropping
number_of_pixel = 0
x_av = 0
y_av = 0

for y in range(result_image.shape[0]):
    for x in range(result_image.shape[1]):
        if (result_image[y, x] == dark_array)[1]:
            number_of_pixel = number_of_pixel + 1
            x_av += x
            y_av += y

x_av = int(x_av / number_of_pixel)
y_av = int(y_av / number_of_pixel)

# #Rule = if you are surrounded by blue pixels you are blue
# for y in range(result_image.shape[0]-1):
#     for x in range(result_image.shape[1]):
#         if (result_image[y,x] != dark_array)[1]:
#             if ((result_image[y+1, x] == dark_array)[1] and
#                 (result_image[y-1, x] == dark_array)[1] and
#                 (result_image[y, x+1] == dark_array)[1] and
#                 (result_image[y+1, x-1] == dark_array)[1]
#             ):
#                     result_image[y, x] = dark_array

# Get the min and max x values
test_col = result_image[y_av, x_av]

x_center = x_av
y_center = y_av

x_max = 0

while True:
    xint = x_max

    for y in range(y_center, 0, -1):
        if (result_image[y, x_center] != test_col)[1]:
            break
        for x in range(x_center, result_image.shape[1]):
            if (result_image[x, y] != test_col)[1]:
                if x > x_max:
                    x_max = x
                    x_max_y = y
                break


    for y in range(y_center, result_image.shape[0]):
        if (result_image[y, x_center] != test_col)[1]:
            break
        for x in range(x_center, result_image.shape[1]):
            if (result_image[y, x] != test_col)[1]:
                if x > x_max:
                    x_max = x
                    x_max_y = y
                break

    x_center = x_max
    y_center = x_max_y
    print(x_max)
    if xint == x_max:
        break

x_center = x_av
y_center = y_av
x_min = result_image.shape[1]

while True:
    xint = x_min
    for y in range(y_center, 0, -1):
        if (result_image[y, x_center] != test_col)[1]:
            break
        for x in range(x_center, 0, -1):
            if (result_image[x, y] != test_col)[1]:
                if x < x_min:
                    x_min = x
                    x_min_y = y
                break

    for y in range(y_center, result_image.shape[0]):
        if (result_image[y, x_center] != test_col)[1]:
            break
        for x in range(x_center, 0, -1):
            if (result_image[y, x] != test_col)[1]:
                if x < x_min:
                    x_min = x
                    x_min_y = y
                break

    x_center = x_min
    y_center = x_min_y
    print(x_min)
    if xint == x_min:
        break

# Gets y_min
x_center = x_min + 1
y_center = x_min_y
y_min = 0

while True:
    yint = y_min

    for x in range(x_min+1, x_max-1):
        if (result_image[y_center, x] != test_col)[1]:
            break
        for y in range(y_center, result_image.shape[0]):
            if (result_image[y, x] != test_col)[1]:
                if y > y_min:
                    y_min = y
                    y_min_x = x
                break

    x_center = y_min_x
    y_center = y_min
    print(y_min)
    if yint == y_min:
        break


# Gets y_max
x_center = x_min + 1
y_center = x_min_y
y_max = result_image.shape[0]

while True:
    yint = y_max

    for x in range(x_min+1, x_max-1):
        for y in range(y_center, 0, -1):
            if (result_image[y, x] != test_col)[1]:
                if y < y_max:
                    y_max = y
                    y_max_x = x
                break

    x_center = y_max_x
    y_center = y_max
    print(y_max)
    if yint == y_max:
        break

# Get the min and max y values
result_image[y_max, y_max_x] = [255, 0, 255]
result_image[y_min, y_min_x] = [255, 0, 255]
result_image[x_max_y, x_max] = [255, 0, 255]
result_image[x_min_y, x_min] = [255, 0, 255]
plt.imshow(result_image)

final_image = result_image[(y_max-10):(y_min+10):, (x_min-10):(x_max+10)]
plt.imshow(final_image)

lake_region_area = get_area(UL_lat, UL_long, LR_lat, LR_long)

count = 0
for y in range(final_image.shape[0]):
    for x in range(final_image.shape[1]):
        if (final_image[y, x] == dark_array)[1]:
            count = count + 1

lake_area = lake_region_area * count / (image.shape[0] * image.shape[1])

from ImageProccessing_core import *
area = main_process(image, lake_region_area, y1, y2, x1, x2, auto_crop=True, vis=True)
print(area)






