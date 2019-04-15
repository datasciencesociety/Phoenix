from lxml.html import fromstring

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
    xmin = xml.xpath("//xmin/text()")
    xmax = xml.xpath("//xmax/text()")
    ymin = xml.xpath("//ymin/text()")
    ymax = xml.xpath("//ymax/text()")
    name = xml.xpath("//name/text()")
    cat = [name2cat(x) for x in name]
    
    row = " ".join([",".join(x) for x in zip(xmin, ymin, xmax, ymax, cat) if x[4] != "other"])
    return filename.replace("xml", "jpg") + " " + row