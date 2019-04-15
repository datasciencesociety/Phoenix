from PIL import Image

def scale(s):
    return int(int(s) * 11.52)

def getBox(data):

    left = scale(data[3])
    top = scale(data[4])
    right = scale(data[5])
    bottom = scale(data[6])
    
    return (left, top, right, bottom)

def createImages(fileName, basefolder):
    
    subFolder = ["/labels/", "/products/"]
    
    f = open(fileName, "r")

    for l in f:
        
        
        data = l.split(",")
        imgName = data[0].split("/")[-1]
        imgName = imgName.replace("_small.jpg", "")
        
        print(imgName)
        
        category = int(data[1])
        
        box = getBox(data)
        
        im = Image.open(basefolder + "/ground_truth/" + imgName + ".jpg")
        im = im.crop(box)
        im.save(basefolder + subFolder[category] + imgName + '_'.join(data[3:7]) + ".jpg")
   

    f.close()
    
if __name__ == '__main__':
    baseFolder = "/home/dimitar/sources/datathon2019/data/Kaufland_DataThon+2019_04_participants"
    
    
    createImages("output.txt", baseFolder)