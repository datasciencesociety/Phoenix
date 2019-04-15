#Base Libraries
import io

#Read Zip File
import zipfile

#Read Images and XMLs
from PIL import Image
import xml.etree.ElementTree as ET

#Visualize Results
import matplotlib.pyplot as plt

#Base Objects
samples = ['ground_truth','working']
data = {"img" : {samples[0] : {}, samples[1] : {}},
            'xml' : {samples[0] : {}, samples[1] : {}}}

#Load kaufland file
kaufland_files = zipfile.ZipFile('Kaufland_DataThon+2019_04_participants.zip','r')


def xml_to_dict(el):
  """
  Concerts XML to Dict. Note that the "object" tag is assigned to key "objects",
  which contains a list of all "object" tags. The "objects" element is placed on 
  the same level as annotation
  """
  my_dict = {}
  objects = []
  
  if(len(list(el))>0):
    my_dict_tmp = {}
    for el_tmp in el:
      if el_tmp.tag == "object":
        objects.append(xml_to_dict(el_tmp))
      else:
        my_dict_tmp.update(xml_to_dict(el_tmp))
    
    if len(objects) > 0:
      my_dict['objects'] = objects
    
    my_dict[el.tag] = my_dict_tmp
  else:
    my_dict[el.tag] = el.text
  
  return my_dict


for name in kaufland_files.namelist():
  for sample in samples:
    if name.startswith(sample):
        if name.endswith(".jpg"):
          data['img'][sample][name[name.rfind("_")+1:name.rfind(".")]] = Image.open(io.BytesIO(kaufland_files.read(name)))
        elif name.endswith(".xml"):
          data['xml'][sample][name[name.rfind("_")+1:name.rfind(".")]] = xml_to_dict(ET.fromstring(kaufland_files.read(name)))

#Check File ID
my_id = list(data['img'][samples[0]].keys())[0]
print("Current ID:", my_id)

#Show Image
plt.imshow(data['img'][samples[0]][my_id])

#Check xml
data['xml'][samples[0]][my_id]

  

