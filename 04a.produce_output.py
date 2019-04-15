from PIL import Image, ImageDraw, ImageFont
from itertools import groupby

from lxml.html import fromstring
import glob

from itertools import groupby


 
def processXMLFile(filename):
    f = open(filename, "r")
    text = f.read()
    f.close()
    
    xml = fromstring(text)
    xmin = map(int, xml.xpath("//xmin/text()"))
    xmax = map(int, xml.xpath("//xmax/text()"))
    ymin = map(int, xml.xpath("//ymin/text()"))
    ymax = map(int, xml.xpath("//ymax/text()"))
    name = xml.xpath("//name/text()")
    
    imgName = filename.replace(".xml", ".jpg").replace("_xml", "")
    
    im = Image.open(imgName)
    draw = ImageDraw.Draw(im)
    
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 60)
    for i, x in enumerate(zip(xmin, ymin, xmax, ymax, name)):
        draw.text((x[0], x[3] + 10), str(i) + " " + x[4], font=fnt, fill=(0, 255, 0))
        draw.text((x[0] + 1, x[3] + 11), str(i) + " " + x[4], font=fnt, fill=(0, 255, 0))
        draw.text((x[0] + 2, x[3] + 12), str(i) + " " + x[4], font=fnt, fill=(0, 255, 0))
        draw.text((x[0] + 3, x[3] + 13), str(i) + " " + x[4], font=fnt, fill=(0, 255, 0))
        draw.line((x[0], x[1], x[0], x[3]), fill=(0, 255, 0), width = 10)
        draw.line((x[0], x[3], x[2], x[3]), fill=(0, 255, 0), width = 10)
        draw.line((x[2], x[3], x[2], x[1]), fill=(0, 255, 0), width = 10)
        draw.line((x[2], x[1], x[0], x[1]), fill=(0, 255, 0), width = 10)
        
    del draw
    
    im.save(imgName.replace("test", "output"))
    
def calCat(name):
    if name.startswith("label_"):
        return 0
    else:
        return 1

def isMisplaced(x, y):
    return (x[2] < y[0]) or (x[0] > y[2])

def isMissing(x, y):
    return (y[2] - y[0]) > 2.3 * (x[2] - x[0])
    
def processXMLFileOutput(filename, results):
    f = open(filename, "r")
    text = f.read()
    f.close()
    
    fn = filename.split("/")[-1]
    
    xml = fromstring(text)
    xmin = map(int, xml.xpath("//xmin/text()"))
    xmax = map(int, xml.xpath("//xmax/text()"))
    ymin = map(int, xml.xpath("//ymin/text()"))
    ymax = map(int, xml.xpath("//ymax/text()"))
    name = xml.xpath("//name/text()")
    cat = map(calCat, name)
    name_new = map(lambda x: x.replace("label_", ""), name)
    
    #for i, x in enumerate(zip(xmin, ymin, xmax, ymax, name, cat)):
    #    print(x)

    for key, group in groupby(zip(xmin, ymin, xmax, ymax, name_new, cat, name), lambda x: x[4]):
        data = [x for x in group]
 
        if len(data) == 1:
            #it is ok
            results.append(",".join([data[0][6],fn, "0"]))
        elif len(data) == 2:
            flag = "0"
            #check for misplaced
            if isMisplaced(data[0], data[1]):
                flag = "1"
            #check for missing
            elif isMissing(data[0], data[1]):
                flag = "1"
               
            for x in data:
                results.append(",".join([x[6],fn, flag]))   
        else:
 
            #check for misplaced
            flag = "0"
            if isMisplaced(data[0], data[1]):
                flag = "1"
            for x in data:
                results.append(",".join([x[6],fn, flag]))
             
            
    
if __name__ == '__main__':
    baseFolder = "/home/dimitar/sources/datathon2019/data/Kaufland_DataThon+2019_04_participants"
    fileNames = glob.glob(baseFolder + "/test_xml/*.xml")
    
    result = []
    for fn in fileNames:
        print(fn)
        processXMLFileOutput(fn, result)
    
    f = open("result.txt", "w")
    f.write("Objects,Files,Values\n")
    f.write("\n".join(result))
    f.close()
    
    
        