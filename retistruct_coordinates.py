import pandas as pd
import os
import math
import scipy.io

# Keep flip DV unchecked
ANIMAL_NUMBER = "3241"
SIDE = "RE"
HOME = "C:/Users/Acer/PycharmProjects/MORF3/DATA/RETISTRUCT/"
MATLAB_PATH = HOME + ANIMAL_NUMBER + " " + SIDE + "/r.mat"
REFERENCE_DEGREE = None
SAVE_DIR = HOME


def excel_from_matlab(path, animal, side, reference_degree=None):
    """
    :param path: path to .mat file from RETISTRUCT
    :param animal: integer number identifier
    :param side: left or right (eye)
    :param reference_degree: If the cuts for a retina are such that Nasal direction
        is within a tear instead of a border edge, another point of reference is chosen.
        Use this parameter as the positive degree that that position points to. For LE,
        zero degrees is temporal and for RE, zero degrees is nasal. Dorsal is always 90.
    :return: a string showing the quadrant that each cell is found in.
    """
    data = scipy.io.loadmat(MATLAB_PATH)
    data = data['Dss'][0][0][0]
    df = pd.DataFrame(data, columns=['Latitude (Radius Radians)', 'Longitude (Theta Radians)'])
    df.index += 1  # index starts at 1 now and is the direct correspondance to cell number

    df['Longitude (Theta Positive Radians)'] = [i + 2 * math.pi if i < 0 else i for i in df['Longitude (Theta Radians)']]
    df['Longitude (Theta Positive Degrees)'] = [round((i * 360) / (2 * math.pi), 1) for i in df['Longitude (Theta ' \
                                                                                                'Positive Radians)']]

    if SIDE.upper() == 'RE':
        df['Theta Degrees in Left Eye Space'] = list(map(lambda x: 180 - x, df['Longitude (Theta Positive Degrees)']))
        df['Theta Degrees in Left Eye Space'] = [i - 360 if i > 360 else i for i in df['Theta Degrees in Left Eye Space']]
        df['Theta Degrees in Left Eye Space'] = [i + 360 if i < 0 else i for i in
                                                 df['Theta Degrees in Left Eye Space']]
        if reference_degree is not None:
            df['Theta Degrees in Left Eye Space'] = [i + reference_degree
                                                     for i in df['Theta Degrees in Left Eye Space']]
            df['Theta Degrees in Left Eye Space'] = [i - 360 if i > 360 else i for i in
                                                     df['Theta Degrees in Left Eye Space']]
    elif SIDE.upper() == 'LE':
        df['Theta Degrees in Left Eye Space'] = df['Longitude (Theta Positive Degrees)']
        if reference_degree is not None:
            df['Theta Degrees in Left Eye Space'] = [i + reference_degree
                                                     for i in df['Theta Degrees in Left Eye Space']]
            df['Theta Degrees in Left Eye Space'] = [i - 360 if i > 360 else i for i in
                                                     df['Theta Degrees in Left Eye Space']]

    else:
        print('Spelling Error')

    def region(angle):
        if 0 < angle < 90:
            return 'DT'
        elif 90 < angle < 180:
            return 'DN'
        elif 180 < angle < 270:
            return 'VN'
        elif 270 < angle < 360:
            return 'VT'
        elif angle == 0 or angle == 360:
            return 'T'
        elif angle == 90:
            return 'D'
        elif angle == 180:
            return 'N'
        elif angle == 270:
            return 'V'
        else:
            return 'ERROR'

    df['Region'] = list(map(region, df['Theta Degrees in Left Eye Space']))

    df.to_excel(SAVE_DIR + f'{ANIMAL_NUMBER}_{SIDE}_RETISTRUCT.xlsx')


excel_from_matlab(MATLAB_PATH, ANIMAL_NUMBER, SIDE, reference_degree=REFERENCE_DEGREE)
