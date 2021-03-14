# Satallite_mapping_OPENCV
Finding surface area of dark bodies using the OPENCV library and publicly avalible satellite imagery 

# Motivation
Remote sensing is revolutionizing data collection and monitoring for remote sites. With very simple tools powerful insights can be gained from publically available data. This project is a tech demo to show how open_cv can be utilized for satellite image processing. The work presented here is not a final product and a very rough implementation. The goal is to estimate the surface area of the lake show below. 

# Features
- Autocropping and image proccessing of satallite images
- (Kinda) accurate area measurements 
- Easily scalable for timeseries data collection 

# Images

![photo_1](https://user-images.githubusercontent.com/78721353/111085680-a5d48180-84d5-11eb-8be0-d226a4568e33.png)

### Figure 1: Raw image from NASA Landsat satallite. Goal is to the estimate the surface area of the large central lake. 

![photo_2](https://user-images.githubusercontent.com/78721353/111085761-f8ae3900-84d5-11eb-8dd2-01c5d37f2b9a.png)

### Figure 2: Image is cropped with the large body at the center. This needs to be done manually to show the program where to measure. 

![photo_3](https://user-images.githubusercontent.com/78721353/111085795-2d21f500-84d6-11eb-833c-8d3a6cf9e456.png)

### Figure 3: K-Mean algorithem applied. 2 clusters of green and blue pixels. 

![photo_4](https://user-images.githubusercontent.com/78721353/111085819-53479500-84d6-11eb-81a9-3e752148d6b6.png)

### Figure 4: Program automatically detects largest dark body and crops the image. Measures number of blue pixels and compares it to given measurements to estimate surface area 

# Code Examples 

First step is loading an image using open cv. Image is loaded inverted (for some reason) needs to be inverted. 
```Python
image = cv2.imread("Photos/LC08_L1TP_051012_20200810_20200810_01_RT.jpg")
image =cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
```

Next we need a geospatial component. I chose to use lattiude and longitude, below are the coordinates for each corner (i.e UL_lat = upper left lattiude.) This data should be easily extracted from the Landsat website.  
```Python
UL_lat = 69.41141
UL_long = -119.06171
LR_lat = 67.08418
LR_long = -113.01863
```

Now need to specify the corners for manual cropping. After viewing the loaded image identify the approximate pixel positions of the dark body. 

```Python
y1 = 5400
y2 = 5700
x1 = 2500
x2 = 2800
```

Now we need to get the total area of the image (in meters): 

```Python
lake_region_area = get_area(UL_lat, UL_long, LR_lat, LR_long)
```

Now calling the main function which will return the area of the body. 

```Python
area = main_process(image, lake_region_area, y1, y2, x1, x2, auto_crop=True, vis=True)
print(area)
```
In this case the output is 6875335.663082852 m^2
