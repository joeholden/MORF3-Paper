import cv2
import pandas as pd
import os
import glob
import datetime
import keyboard
import re

"""
This program allows you to start from your last location each time.
If you have analyzed some images so far, the program reads in your previous data sheet and looks at each image filename
to see if it has been processed already. Only new images are processed. A new excel sheet is added each time so you
don't have to worry about overwriting any existing data by accident. 
"""
# Only Modify the HOME Directory
HOME = "C:/Users/joema/Desktop/Individual Retina Data/3231 RE/"

IMGS_DIR = HOME + "Vessel and V5 PNGs/"
EXCEL_DIR = HOME + "Excel Sheets/"
RESOLUTION = 6.4455


def vessel_diameter(image_path, resolution):
    """
    Loads and image and displays it using OpenCV. Program awaits mouse clicks to lock in coordinates for the width
    of a blood vessel. Left click to lock in the first coordinate and right click to lock in the second. At this point,
    a line should be completed. Now the program is awaiting a keyboard event to determine how to proceed. If 'W' is
    pressed, the user is allowed to add another vessel. Unlimited number of vessels can be added. If 'Q' is pressed,
    the function ends and returns an array of diameters of the vessels and the image path.
    """
    image = cv2.imread(image_path)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    width = int(image.shape[1] * .90)
    height = int(image.shape[0] * .90)
    cv2.resizeWindow("image", width, height)

    x1, x2, y1, y2, mouse_x, mouse_y = None, None, None, None, None, None
    diameters = []
    all_points = []

    q_pressed = False
    w_pressed = False

    def on_mouse(event, x, y, flags, param):
        nonlocal x1, x2, y1, y2, mouse_x, mouse_y, all_points
        if event == cv2.EVENT_MOUSEMOVE:
            mouse_x, mouse_y = x, y
            # print(mouse_x, mouse_y)
        if event == cv2.EVENT_LBUTTONDOWN:
            x1, y1, = x, y

        if event == cv2.EVENT_RBUTTONDOWN:
            x2, y2 = x, y

        if x1 is not None and x2 is not None:  # this is adding a combination of x and y values it should not
            if (x1, y1, x2, y2) not in all_points:
                all_points.append((x1, y1, x2, y2))

    cv2.setMouseCallback('image', on_mouse)

    while True:
        # Load in a copy of the original image so the line you draw doesn't leave traces
        image_c = image.copy()

        # Re Draw Points and Line each time the image refreshes
        if x1 is not None or x2 is not None:
            cv2.circle(image_c, (x1, y1), 3, (0, 255, 255), -1)
            cv2.circle(image_c, (x2, y2), 3, (0, 255, 255), -1)
            cv2.line(image_c, (x1, y1), (mouse_x, mouse_y), color=(0, 255, 255), thickness=2)

        # Draw Lines from Previous Runs
        for line in all_points:
            cv2.line(image_c, (line[0], line[1]), (line[2], line[3]), color=(0, 255, 255), thickness=2)

        cv2.imshow('image', image_c)

        if x2 is not None:
            while not q_pressed or not w_pressed:
                k = cv2.waitKey(20) & 0xFF
                if k == 27:
                    break
                if k == 113:
                    q_pressed = True
                    length = pow(pow(x2-x1, 2) + pow(y2-y1, 2), 1/2)
                    diameters.append(round(length / resolution, 1))
                    break
                if k == 119:
                    w_pressed = True
                    length = pow(pow(x2-x1, 2) + pow(y2-y1, 2), 1/2)
                    diameters.append(round(length / resolution, 1))
                    break

        if w_pressed:
            x1, x2, y1, y2, mouse_x, mouse_y = None, None, None, None, None, None
            w_pressed = False
        if q_pressed:
            break

        k = cv2.waitKey(20) & 0xFF

        if k == 27:
            break
        elif k == ord('a'):
            print(mouse_x, mouse_y)

    return diameters, image_path


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
    list_of_files = glob.glob(EXCEL_DIR + 'Vessel Diameters/*')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_excel(latest_file, index_col='Unnamed: 0')
except ValueError:
    df = pd.DataFrame()

for root, dirs, files in os.walk(IMGS_DIR):
    for file in files:
        image_path = os.path.join(root, file).split("/")[-1]
        id = re.search(pattern=r"/(\d+) (\w+)/Vessel and V5 PNGs/", string=root)
        identifier = id[1] + "_" + id[2] + "_" + image_path.strip(".png")

        if identifier in df.columns:
            print(identifier)
            continue
        else:
            v_diameters, image_path = vessel_diameter(image_path=os.path.join(root, file), resolution=RESOLUTION)
            v_diameters = pd.Series(v_diameters)
            image_path = image_path.split('/')[-1].strip('.png')
            id = re.search(pattern=r"/(\d+) (\w+)/Vessel and V5 PNGs/", string=root)
            identifier = id[1] + "_" + id[2] + "_" + image_path
            new_df = pd.DataFrame(v_diameters, columns=[identifier])
            df = pd.concat([df, new_df], axis=1)
            print('Run Another? yes: 1, n: 0?\n')
            key = choice_to_continue()
            if key == 0:
                break

df.to_excel(EXCEL_DIR + f'Vessel Diameters/Diameters_{datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.xlsx')
print(df.T)