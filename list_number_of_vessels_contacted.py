import cv2
import pandas as pd
import os
import glob
import datetime
import keyboard

"""
This is best run from the terminal since it requires user input that would otherwise write to this file.
This script simply opens images and allows you to count the number of vessels an astrocyte is contacting.
Everything is output to a excel sheet and can be done in multiple sittings.
Type the number of vessels on your keyboard followed by a 1 (continue) or 0 (exit)
"""

# Only Modify the HOME Directory
HOME = "C:/Users/joema/Desktop/home/3041 LE/"

IMGS_DIR = HOME + "Vessel and V5 PNGs/"
EXCEL_DIR = HOME + "Excel Sheets/Vessel Counts/11"
RESOLUTION = 6.4455


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
    list_of_files = glob.glob(EXCEL_DIR + '*')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_excel(os.path.join(EXCEL_DIR, latest_file), index_col='Unnamed: 0')
except ValueError:
    df = pd.DataFrame()

for root, dirs, files in os.walk(IMGS_DIR):
    for file in files:
        if file in df.columns:
            continue
        else:
            image = cv2.imread(os.path.join(root, file))
            cv2.imshow(f'{os.path.join(root, file)}', image)

            k = cv2.waitKey()
            print(f'There were {chr(k)} vessels. Run Another? yes: 1, n: 0?\n')
            cv2.destroyAllWindows()

            new_df = pd.DataFrame(pd.Series(chr(k)), columns=[f'{file}'])
            df = pd.concat([df, new_df], axis=1)

            key = choice_to_continue()
            if key == 0:
                cv2.destroyAllWindows()
                break


df.to_excel(EXCEL_DIR + f'Number_of_Vessels_Contacted_{datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.xlsx')


