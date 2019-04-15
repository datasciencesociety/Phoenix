import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import cv2

def loadFiles(fileName):
    result = []
    f = open(fileName, "r")

    for l in f:
        result.append(l.split(" ")[0])
    f.close()
    
    return result


def processImage(yolo, fileName, result):
    
    vid = cv2.VideoCapture(fileName)
    return_value, frame = vid.read()

    image = Image.fromarray(frame)
    
    image, out_boxes, out_scores, out_classes = yolo.detect_image(image)
    
    for x, c in enumerate(out_classes):
        top, left, bottom, right = out_boxes[x]
        top = str(max(0, int(top)))
        left = str(max(0, int(left)))
        bottom = str(min(320, int(bottom)))
        right = str(min(416, int(right)))
        box = [left, top, right, bottom]
        row = [fileName, str(out_classes[x]), str(out_scores[x])] + box
        result.append(",".join(row))
    
    
    
if __name__ == '__main__':
    files = loadFiles("/home/d-vasilev/keras-yolo3/train.txt")
    result = []
    yolo = YOLO()
    for fn in files:
        processImage(yolo, fn, result)
    f = open("output.txt", "w")
    f.write("\n".join(result))
    f.close()

