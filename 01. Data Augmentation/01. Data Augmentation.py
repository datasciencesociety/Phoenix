import io
import math
import numpy as np
import os
import pickle

#Read Zip File
import zipfile

#Read Images and XMLs
from PIL import Image, ImageFilter
import xml.etree.ElementTree as ET

#Visualize Results
import matplotlib.pyplot as plt
%matplotlib inline

#Use this to resize before visualization
def show_image(img):
  img = img.copy()
  img.thumbnail((461,346), Image.ANTIALIAS)
  plt.imshow(img)
  plt.show()

#Base Objects
samples = ['ground_truth','working']
data = {"img" : {samples[0] : {}, samples[1] : {}},
            'xml' : {samples[0] : {}, samples[1] : {}}}

data_background = {}

#=================================================================
#Load kaufland file
#=================================================================
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


#=================================================================
#Check File ID
#=================================================================
my_id = list(data['img'][samples[0]].keys())[20]
print("Current ID:", my_id)
show_image(data['img'][samples[0]][my_id])  
#Check xml
len(data['xml'][samples[0]][my_id]['objects'])


#=================================================================
idx = 0
#=================================================================



#=================================================================
#Check all IDs
#=================================================================
my_id = list(data['img'][samples[0]].keys())[idx]
print("Currentrrent ID:", my_id)
show_image(data['img'][samples[0]][my_id])




#=================================================================
#Try Background
#=================================================================
start_y = 600
start_x = 2100
store = data['img'][samples[0]][my_id].crop([start_x,start_y,start_x+200,start_y+200])
show_image(store)




#=================================================================
#Store Final Background
#=================================================================
data_background[my_id] = store
idx += 1
  
#Validate Results
for i in list(data_background.keys()):
  if i not in list(data['img'][samples[0]].keys()):
    print(i)
  
#Store pickle
pickle.dump(data_background, open("dat_background.pkl", "wb" ) )





#=================================================================
# Remove objects
#=================================================================
def check_intersection(first, second):
    return not (first[2] < second[0] or \
                    first[0] >  second[2] or \
                    first[3] < second[1] or \
                    first[1] > second[3])


def fill_space(img, pos, background):
  mult_width = math.ceil((pos[2]-pos[0])/background.size[0])
  mult_height = math.ceil((pos[3]-pos[1])/background.size[1])
  
  total_width = background.size[0]*mult_width
  total_height = background.size[1]*mult_height

  new_im = Image.new('RGB', (total_width, total_height))

  y_offset = 0
  for k in range(mult_height):
      x_offset = 0
      for i in range(mult_width):
          new_im.paste(background, (x_offset,y_offset))
          x_offset += background.size[0]

      y_offset += background.size[1]


  fill_image = new_im.crop([0,0,pos[2]-pos[0], pos[3]-pos[1]])
  
  img.paste(fill_image, pos)

def remove_object(img, object_idx, objects, background):
  remove_object_list = [object_idx]
  object_pos = [int(x) for x in objects[object_idx]['object']['bndbox'].values()]
  
  for i in range(len(objects)):
    object_pos_sec = [int(x) for x in objects[i]['object']['bndbox'].values()]
    
    if check_intersection(object_pos, object_pos_sec) and \
        objects[i]['object']['name'].startswith("label") == False:
        
        remove_object_list.append(i)

  for i in remove_object_list:
    fill_space(img, 
                [int(x) for x in objects[i]['object']['bndbox'].values()],
                background)
  
  return img, [i for j, i in enumerate(objects) if j not in remove_object_list]



#=================================================================
# Generate Images - Remove Objects
#=================================================================
sample = samples[0]
sample_size = 500
image_folder = "Images"

for i in range(1, sample_size + 1):
  image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
  my_id = list(data['img'][sample].keys())[image_idx]

  image = data['img'][sample][my_id].copy()
  objects = data['xml'][sample][my_id]['objects'].copy()

  object_idx = np.random.randint(0, high=len(data['xml'][sample][my_id]['objects'])-1)

  hold_processing = True
  counter = 0
  while hold_processing:
    is_label = objects[object_idx]['object']['name'].startswith("label")

    if is_label == False:
      hold_processing = False
    else:
      counter += 1
      if counter >= 20:
        image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
        my_id = list(data['img'][sample].keys())[image_idx]

        image = data['img'][sample][my_id].copy()
        objects = data['xml'][sample][my_id]['objects'].copy()


      object_idx = np.random.randint(0, high=len(data['xml'][sample][my_id]['objects'])-1)
  
  
  image, objects = remove_object(image, object_idx, objects, data_background[my_id])
  
  skip = False
  if i >= 300:
      object_idx = np.random.randint(0, high=len(objects)-1)
      
      hold_processing = True
      counter = 0
      while hold_processing:
        is_label = objects[object_idx]['object']['name'].startswith("label")
        
        if is_label == False:
          hold_processing = False
        else:
          counter += 1
          if counter >= 20:
            skip = True
            break
          else:
            object_idx = np.random.randint(0, high=len(objects)-1)
      
      if skip == False:
        image, objects = remove_object(image, object_idx, objects, data_background[my_id])
        
          
  if i >= 450 and skip == False:
      object_idx = np.random.randint(0, high=len(objects)-1)
      
      hold_processing = True
      counter = 0
      while hold_processing:
        is_label = objects[object_idx]['object']['name'].startswith("label")
        
        if is_label == False:
          hold_processing = False
        else:
          counter += 1
          if counter >= 20:
            skip = True
            break
          else:
            object_idx = np.random.randint(0, high=len(objects)-1)
      
      if skip == False:
        image, objects = remove_object(image, object_idx, objects, data_background[my_id])
  
  
  image.save(os.path.join(image_folder, "remove1_" + str(i) + ".jpg"))
  pickle.dump(objects, open(os.path.join(image_folder, "remove1_" + str(i) + ".pkl"), "wb" ) )

  

#=================================================================
# Get Label bounds
#=================================================================
def get_label_bounds(objects):
    label_bounds = []
    for my_object in objects:
        if my_object['object']['name'].startswith("label"):

            ymax = int(my_object['object']['bndbox']['ymax'])
            ymin = int(my_object['object']['bndbox']['ymin'])

            if len(label_bounds) == 0:
                label_bounds.append([ymin, ymax])
            else:
                ok_flag = 0
                for value in label_bounds:
                    if value[1] >= ymax and value[0] <= ymin:
                        ok_flag = 1
                    elif value[1] < ymax and value[1] >= ymin and value[0] <= ymin:
                        value[1] = ymax
                        ok_flag = 1
                    elif value[1] >= ymax and value[0] <= ymax and value[0] > ymin:
                        value[0] = ymin
                        ok_flag = 1
                    elif value[1] < ymax and value[0] > ymin:
                        value[1] = ymax
                        value[0] = ymin
                        ok_flag = 1
                        
                if ok_flag == 0:
                    label_bounds.append([ymin, ymax])
    return label_bounds

#=================================================================
# Generate Images - Add Objects
#=================================================================
imgs = []
for f in os.listdir(image_folder):
    if f.endswith(".jpg") and "remove" in f:
      imgs.append(os.path.join(image_folder, f))

for idx in range(501, 1001):
  print("Image:", str(idx))
  #Load Augmented Image
  img_path = np.random.choice(imgs)
  image = Image.open(img_path)
  objects = pickle.load(open(img_path[:-4]+".pkl", "rb" ))
  
  #=========================================================================
  #Get Object to place inside augmented image
  #=========================================================================
  image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
  my_id = list(data['img'][sample].keys())[image_idx]

  image_extr = data['img'][sample][my_id].copy()
  objects_extr = data['xml'][sample][my_id]['objects'].copy()
  
  object_idx = np.random.randint(0, high=len(objects_extr)-1)

  hold_processing = True
  counter = 0
  while hold_processing:
    is_label = objects_extr[object_idx]['object']['name'].startswith("label")

    if is_label == False:
      hold_processing = False
    else:
      counter += 1
      if counter >= 20:
        image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
        my_id = list(data['img'][sample].keys())[image_idx]

        image_extr = data['img'][sample][my_id].copy()
        objects_extr = data['xml'][sample][my_id]['objects'].copy()

      object_idx = np.random.randint(0, high=len(objects_extr)-1)
    if counter > 500:
      print("ERROR1")
  
  object_pos = [int(x) for x in objects_extr[object_idx]['object']['bndbox'].values()]
  object_extr = objects_extr[object_idx]
  
  image_extr = image_extr.crop(object_pos)
  
  #=========================================================================
  #Find best place
  #=========================================================================
  search_for_place = True
  iters = 0
  while search_for_place:
    if iters > 500:
      print("ERROR2")
    iters += 1
    if iters % 20 == 0:
      img_path = np.random.choice(imgs)
      image = Image.open(img_path)
      objects = pickle.load(open(img_path[:-4]+".pkl", "rb" ))
    if iters % 50 == 0:
      #=========================================================================
      #Get Object to place inside augmented image
      #=========================================================================
      image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
      my_id = list(data['img'][sample].keys())[image_idx]

      image_extr = data['img'][sample][my_id].copy()
      objects_extr = data['xml'][sample][my_id]['objects'].copy()

      object_idx = np.random.randint(0, high=len(objects_extr)-1)

      hold_processing = True
      counter = 0
      while hold_processing:
        is_label = objects_extr[object_idx]['object']['name'].startswith("label")

        if is_label == False:
          hold_processing = False
        else:
          counter += 1
          if counter >= 20:
            image_idx = np.random.randint(0, high=len(data['img'][sample])-1)
            my_id = list(data['img'][sample].keys())[image_idx]

            image_extr = data['img'][sample][my_id].copy()
            objects_extr = data['xml'][sample][my_id]['objects'].copy()

          object_idx = np.random.randint(0, high=len(objects_extr)-1)
        if counter > 500:
          print("ERROR3")

      object_pos = [int(x) for x in objects_extr[object_idx]['object']['bndbox'].values()]
      object_extr = objects_extr[object_idx]

      image_extr = image_extr.crop(object_pos)      
    
    counter = 0
    search_ref_object = True
    while search_ref_object:
      ref_object = np.random.choice(objects)
      if ref_object['object']['name'].startswith("label")==False:
        break
      else:
        counter += 1
        
        if counter > 20:
          img_path = np.random.choice(imgs)
          image = Image.open(img_path)
          objects = pickle.load(open(img_path[:-4]+".pkl", "rb" ))
          
      if counter > 500:
        print("ERROR4")
      
      
    ref_pos = [int(x) for x in ref_object['object']['bndbox'].values()]
    
    
    label_bounds = get_label_bounds(objects)
    
    
    #Pick vertical start
    if len(label_bounds)==1:
      vertical_start = label_bounds[0]
    else:
      vertical_start_idx = np.random.randint(0, high=len(label_bounds)-1)
      vertical_start = label_bounds[vertical_start_idx]
    
    #Pick horizontal adjustments
    horiz_adj = np.random.choice([30, 50, 100, 200, 500])
    if np.random.rand() < 0.5:
      placement = [ref_pos[0]-horiz_adj-image_extr.size[0],
                    vertical_start[0]-20-image_extr.size[1],
                    ref_pos[0]-horiz_adj,
                    vertical_start[0]-20]
      if np.min(placement) < 0:
        continue
    else:
      placement = [ref_pos[2]+horiz_adj,
                    vertical_start[0]-20-image_extr.size[1],
                    ref_pos[2]+horiz_adj+image_extr.size[0],
                    vertical_start[0]-20]
      if np.min(placement) < 0 or \
            ref_pos[2]+30+image_extr.size[0] > 4608:
          continue
    
    finish = True
    for i in range(len(objects)):
      object_pos_sec = [int(x) for x in objects[i]['object']['bndbox'].values()]
      
      if check_intersection(placement, object_pos_sec) == True:
        finish = False
    
    if finish == True:
      image.paste(image_extr, placement)
      objects.append(object_extr)
      break
  
  image.save(os.path.join(image_folder, "add1_" + str(idx) + ".jpg"))
  pickle.dump(objects, open(os.path.join(image_folder, "add1_" + str(idx) + ".pkl"), "wb" ) )
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  