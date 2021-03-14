import cv2
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj
# ------------------ Image Processing
# Kmeans: Import a cv2 image will run cluster

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
# get_dark_array: Returns the darkest color in an image


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
# ------------------ Area Calculation


def get_area(UL_lat, UL_long, LR_lat, LR_long):
    myProj = Proj("+proj=utm +zone=23K, +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs")

    UL_UTMx, UL_UTMy = myProj(UL_long, UL_lat)
    LR_UTMx, LR_UTMy = myProj(LR_long, LR_lat)

    total_area = (UL_UTMx - LR_UTMx) * (UL_UTMy - LR_UTMy)
    return total_area
# ------------------ Get max and min locations


def get_xmax(x_av, y_av, img, test_col):
    x_center = x_av
    y_center = y_av
    x_max = 0

    while True:
        xint = x_max

        for y in range(y_center, 0, -1):
            if (img[y, x_center] != test_col)[1]:
                break
            for x in range(x_center, img.shape[1]):
                if (img[x, y] != test_col)[1]:
                    if x > x_max:
                        x_max = x
                        x_max_y = y
                    break
        for y in range(y_center, img.shape[0]):
            if (img[y, x_center] != test_col)[1]:
                break
            for x in range(x_center, img.shape[1]):
                if (img[y, x] != test_col)[1]:
                    if x > x_max:
                        x_max = x
                        x_max_y = y
                    break

        x_center = x_max
        y_center = x_max_y
        if xint == x_max:
            break
    return [x_max, x_max_y]


def get_xmin(x_av, y_av, img, test_col):
    x_center = x_av
    y_center = y_av
    x_min = img.shape[1]

    while True:
        xint = x_min
        for y in range(y_center, 0, -1):
            if (img[y, x_center] != test_col)[1]:
                break
            for x in range(x_center, 0, -1):
                if (img[x, y] != test_col)[1]:
                    if x < x_min:
                        x_min = x
                        x_min_y = y
                    break
        for y in range(y_center, img.shape[0]):
            if (img[y, x_center] != test_col)[1]:
                break
            for x in range(x_center, 0, -1):
                if (img[y, x] != test_col)[1]:
                    if x < x_min:
                        x_min = x
                        x_min_y = y
                    break
        x_center = x_min
        y_center = x_min_y
        if xint == x_min:
            break
    return [x_min, x_min_y]


def get_ymin(x_min, x_max, x_min_y, img, test_col):
    x_center = x_min + 1
    y_center = x_min_y
    y_min = 0
    while True:
        yint = y_min

        for x in range(x_min+1, x_max-1):
            if (img[y_center, x] != test_col)[1]:
                break
            for y in range(y_center, img.shape[0]):
                if (img[y, x] != test_col)[1]:
                    if y > y_min:
                        y_min = y
                        y_min_x = x
                    break
        x_center = y_min_x
        y_center = y_min
        if yint == y_min:
            break
    return y_min


def get_ymax(x_min, x_max, x_max_y, img, test_col):
    x_center = x_min + 1
    y_center = x_max_y
    y_max = img.shape[0]
    while True:
        yint = y_max
        for x in range(x_min+1, x_max-1):
            for y in range(y_center, 0, -1):
                if (img[y, x] != test_col)[1]:
                    if y < y_max:
                        y_max = y
                        y_max_x = x
                    break
        x_center = y_max_x
        y_center = y_max
        if yint == y_max:
            break
    return y_max


# ----------------- Main
def main_process(image, total_area, y1, y2, x1, x2, k=2, auto_crop=True, vis=False):
    image_cropped = image[y1:y2, x1:x2]
    result_image = kmeans(image_cropped, k, show=False)
    dark_array = get_dark_array(result_image)

    if auto_crop:
        # Get the average location of the dark color
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

        test_col = result_image[y_av, x_av]

        xmax, xmaxy = get_xmax(x_av, y_av, result_image, test_col)
        xmin, xminy = get_xmin(x_av, y_av, result_image, test_col)
        ymin = get_ymin(xmin, xmax, xminy, result_image, test_col)
        ymax = get_ymax(xmin, xmax, xmaxy, result_image, test_col)

        final_image = result_image[(ymax-10):(ymin+10):, (xmin-10):(xmax+10)]
    else:
        final_image = result_image

    if vis:
        plt.imshow(final_image)

    count = 0
    for y in range(final_image.shape[0]):
        for x in range(final_image.shape[1]):
            if (final_image[y, x] == dark_array)[1]:
                count = count + 1

    lake_area = total_area * count / (image.shape[0] * image.shape[1])
    return lake_area

# Implementaiton
image = cv2.imread("Photos/LC08_L1TP_051012_20200810_20200810_01_RT.jpg")
image =cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

# -------- Img properties
# Corners of the sat image
UL_lat = 69.41141
UL_long = -119.06171
LR_lat = 67.08418
LR_long = -113.01863












