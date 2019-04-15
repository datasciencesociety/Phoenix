from PIL import Image, ImageDraw
from itertools import groupby

import imgaug as ia
from imgaug import augmenters as iaa
import imageio

def scale(s):
    return int(int(s))

def getBox(data):

    left = scale(data[3])
    top = scale(data[4])
    right = scale(data[5])
    bottom = scale(data[6])
    
    return (left, top, right, bottom)

def createImages(fileName, basefolder):
    
    
    f = open(fileName, "r")

    data = [l.split(",") for l in f]
    
    for key, group in groupby(data, lambda x: x[0]):
        
        imgName = key.split("/")[-1]
        # imgName = imgName.replace("_small.jpg", "")
        print(imgName)
        im = Image.open(basefolder + "/ground_truth/" + imgName)
        draw = ImageDraw.Draw(im)
        
        for thing in group:
            left, top, right, bottom = getBox(thing)
            
            draw.line((left, top, left, bottom), fill=(0, 255, 0), width = 4)
            draw.line((left, bottom, right, bottom), fill=(0, 255, 0), width = 4)
            draw.line((right, top, right, bottom), fill=(0, 255, 0), width = 4)
            draw.line((right, top, left, top), fill=(0, 255, 0), width = 4)
        del draw

        im.save(basefolder + "/bounded/" + imgName)
   

    f.close()
    
if __name__ == '__main__':
    baseFolder = "/home/dimitar/sources/datathon2019/data/Kaufland_DataThon+2019_04_participants"
    
    
    createImages("output.txt", baseFolder)