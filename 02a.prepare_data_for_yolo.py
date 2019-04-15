from lxml.html import fromstring
import glob

from PIL import Image
from resizeimage import resizeimage
from sklearn.cluster import KMeans

def resizeImg(folder):
    fileNames = glob.glob(folder + "/*.jpg")
    
    
    for fileName in fileNames:
        imgId = fileName.split("/")[-1].split(".")[0]
        with open(fileName, 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_cover(image, [400, 300])
                cover.save(folder + "/" + imgId + "_small.jpg", image.format)
                
def name2cat(x):
    if x.startswith("label"):
        return "0"
    elif x.isnumeric():
        return "1"
    else:
        return "other"
    
def processFile(filename):
    f = open(filename, "r")
    text = f.read()
    f.close()
    
    xml = fromstring(text)
    xmin = map(scaleSize, xml.xpath("//xmin/text()"))
    xmax = map(scaleSize, xml.xpath("//xmax/text()"))
    ymin = map(scaleSize, xml.xpath("//ymin/text()"))
    ymax = map(scaleSize, xml.xpath("//ymax/text()"))
    name = xml.xpath("//name/text()")
    cat = [name2cat(x) for x in name]
    
    row = " ".join([",".join(x) for x in zip(xmin, ymin, xmax, ymax, cat) if x[4] != "other"])
    return filename.replace(".xml", "_small.jpg").replace("_xml", "") + " " + row

def scaleSize(x):
    return str(int(int(x) / 11.52))

def loadGroundTruth(folder):
    fileNames = glob.glob(folder + "_xml/*.xml")
    
    return "\n".join([processFile(fileName) for fileName in fileNames])

def calcAnchors(folder):
    result = []
    fileNames = glob.glob(folder + "_xml/*.xml")
    
    for fileName in fileNames:
        x = processAnchor(fileName)
        result += x
        
    return result

def processAnchorTupple(x):
    return int(int(x[0]) / 11.52) - int(int(x[1]) / 11.52)

def processAnchor(filename):
    f = open(filename, "r")
    text = f.read()
    f.close()
    
    xml = fromstring(text)
    xmin = xml.xpath("//xmin/text()")
    xmax = xml.xpath("//xmax/text()")
    ymin = xml.xpath("//ymin/text()")
    ymax = xml.xpath("//ymax/text()")
    
    x = [processAnchorTupple(d) for d in zip(xmax, xmin)]
    y = [processAnchorTupple(d) for d in zip(ymax, ymin)]
    return [z for z in zip(x, y)]
                
if __name__ == '__main__':
    baseFolder = "/home/dimitar/sources/datathon2019/data/Kaufland_DataThon+2019_04_participants/working"
    
    #resize files
    resizeImg(baseFolder)
    
    #prepare training file for yolo
    data = loadGroundTruth(baseFolder)
    f = open("train.txt", "w")
    f.write(data)
    f.close()
    
    #calc ancors
    anc = calcAnchors(baseFolder)
    kmeans = KMeans(n_clusters=10, random_state=0).fit(anc)
    f = open("ancors.txt", "w")
    f.write(", ".join([",".join(map(str, map(int, x))) for x in kmeans.cluster_centers_]))
    f.close()
    
    #calc anchors
    