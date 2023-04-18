import cv2
from contour_functions import centroid
import pandas as pd
import keyboard
import glob
import os
import datetime

"""
This program allows you to measure the distance from the centroid of an ROI 
for an astrocyte to the closest blood vessel.

It allows you to start from your last location each time. If you have analyzed some images so far, the program reads
in your previous data sheet and looks at each image filename to see if it has been processed already. Only new images 
are processed. A new excel sheet is added each time so you don't have to worry about overwriting any existing data 
by accident. 

ROIs need to be named as the image file name is.
Example:
    Image Name: '5.png'
    ROI Name: '5.png.roi'

Press q when the circle touches a vessel (min radius)
Press escape to terminate for some reason.
"""
# Only Modify the HOME Directory
HOME = "C:/Users/joema/Desktop/home/3041 LE/"

IMGS_DIR = HOME + "Vessel and V5 PNGs/"
EXCEL_DIR = HOME + "Excel Sheets/"
ROI_PATH = HOME + "ROIs/"
RESOLUTION = 6.4455


def vessel_distance(roi_path, image_path, resolution):
    """
    Loads in an image with the astrocyte and vessels
    Displays the image and a circle around the centroid of the ROI provided.
    Slider allows you to alter the radius of the circle.
    Press q when the circle touches a vessel (min radius)
    Press escape to terminate for some reason.
    """

    def dummy(var):
        pass

    cv2.destroyAllWindows()
    xc, yc = centroid(roi_path)
    image = cv2.imread(image_path)
    cv2.namedWindow('Astrocyte Centroid')
    cv2.createTrackbar('Radius', 'Astrocyte Centroid', 250, 1000, dummy)  # 50 is the initialization value for the bar

    end = False
    previous_slider_position = 0
    pressed_q = False
    end_radius_px = None

    while not end:
        current_slider = cv2.getTrackbarPos("Radius", "Astrocyte Centroid")
        if current_slider != previous_slider_position:
            rgb = image.copy()

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        slider_val = cv2.getTrackbarPos("Radius", "Astrocyte Centroid")
        cv2.circle(rgb, (xc, yc), slider_val, (255, 0, 255), thickness=3)

        cv2.imshow('Astrocyte Centroid', rgb)

        # Create Key Bindings to Output Radius Value
        if k == 113:  # key 'q'
            print(f'Radius px: {slider_val}\nRadius um: {round(slider_val / resolution, 1)}')
            pressed_q = True
            end_radius_px = slider_val

        if pressed_q:
            end = True

    print(end_radius_px)
    print(resolution)
    try:
        return end_radius_px, round((end_radius_px / resolution), 1), image_path
    except TypeError:
        return None, None, None  # If you hit escape during the image acquisition, this is triggered


def choice_to_continue():
    while True:
        a = keyboard.read_key()

        if a == '1':
            return 1
        if a == '0':
            return 0


# If execution of the program was stopped at some point, we want to be able to
# process the rest of the files without repeats
try:
    list_of_files = glob.glob(EXCEL_DIR + "Distance to Vessel/*")  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_excel(EXCEL_DIR + "Distance to Vessel/" + latest_file, index_col='Unnamed: 0')
except ValueError:
    df = pd.DataFrame(columns=['Image', 'Radius (um)'])

for root, dirs, files in os.walk(IMGS_DIR):
    for file in files:
        if os.path.join(root, file) in list(df['Image']):
            continue
        else:
            rad_px, rad_um, img_path = vessel_distance(roi_path=os.path.join(ROI_PATH, "Convex Hull/convex_hull_" +
                                                                             file.replace(".png", ".nd2") + ".roi"),
                                                       image_path=os.path.join(root, file),
                                                       resolution=RESOLUTION)
            new_df = pd.DataFrame([[img_path, rad_um]], columns=['Image', 'Radius (um)'])
            if (rad_px, rad_um, img_path) != (None, None, None):
                df = pd.concat([df, new_df], axis=0, ignore_index=True)
            print(df)
            print('Run Another? yes: 1, n: 0?\n')
            key = choice_to_continue()
            if key == 0:
                break

print(df)
df.to_excel(EXCEL_DIR + f'Distance to Vessel/Distances to Closest Vessel_{datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.xlsx')



