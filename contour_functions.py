import cv2
from roifile2 import ImagejRoi
from shapely.geometry import Polygon


def centroid(roi_path, image_path=None, show=False):
    """returns the centroid of the given roi (xc, yc).
    If an image_path is provided and show=True, the value is printed and shown on the image"""
    roi = ImagejRoi.fromfile(roi_path)
    coordinates = roi.integer_coordinates

    outline = Polygon(coordinates)
    xc = int(outline.centroid.x) + roi.left
    yc = int(outline.centroid.y) + roi.top

    if show:
        print(xc, yc)
        image = cv2.imread(image_path)
        cv2.circle(image, (xc, yc), 3, (255, 255, 255), thickness=3)
        cv2.imshow('i', image)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return xc, yc



