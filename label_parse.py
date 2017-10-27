import os
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image
import xmltodict
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

# anno_dir = [r"C:\Users\ALuo\PycharmProjects\CVphone\Annotations\users\tohme\cellphones\iphone3gs",
#             r"C:\Users\ALuo\PycharmProjects\CVphone\Annotations\users\tohme\cellphones\samsung_s4_active",
#             r"C:\Users\ALuo\PycharmProjects\CVphone\Annotations\users\tohme\cellphones\xiaomi_note"]

anno_dir = [r"C:\Users\ALuo\PycharmProjects\CVphone\1_Annotations\users\tohme\cellphones\iphone3gs"]
anno_files = [list(map(lambda x: os.path.join(a,x),os.listdir(a))) for a in anno_dir]
anno_files = sum(anno_files, [])
obj_set = set()
for i in range(len(anno_files)):
    with open(anno_files[i], "rb") as xml_file:
        xml_content = xml_file.read()
    parsed = xmltodict.parse(xml_content)
    y,x = int(parsed["annotation"]["imagesize"]["nrows"]), int(parsed["annotation"]["imagesize"]["ncols"])
    num_obj = len(parsed["annotation"]["object"])
    if type(parsed["annotation"]["object"]) is list:
        for j in range(num_obj):
            if parsed["annotation"]["object"][j]["deleted"] in ["1", 1]:
                continue
            if "assembly" in parsed["annotation"]["object"][j]["name"].lower():
                continue
            current_name = ""
            if "camera" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            elif "back" not in parsed["annotation"]["object"][j]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            else:
                current_name = parsed["annotation"]["object"][j]["name"].lower()
            obj_set.add(current_name)
    else:
        if "assembly" not in parsed["annotation"]["object"]["name"].lower() and parsed["annotation"]["object"]["deleted"] not in ["1", 1]:
            if "camera" in parsed["annotation"]["object"]["name"].lower():
                current_name = "camera"
            elif "back" not in parsed["annotation"]["object"]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            else:
                current_name = parsed["annotation"]["object"]["name"].lower()
            obj_set.add(current_name)

num_unique_objs = len(obj_set)
unique_objs = list(obj_set)
print(unique_objs)
def extract_poly(dict_input):
    points = []
    poly = dict_input["polygon"]["pt"]
    for pt_coor in poly:
        points.append((int(pt_coor["x"]), int(pt_coor["y"])))
    points.append(points[0])
    return points

for i in range(len(anno_files)):
    with open(anno_files[i], "rb") as xml_file:
        xml_content = xml_file.read()
    parsed = xmltodict.parse(xml_content)
    y,x = int(parsed["annotation"]["imagesize"]["nrows"]), int(parsed["annotation"]["imagesize"]["ncols"])
    labels_container = np.zeros((num_unique_objs,y,x))

    num_obj = len(parsed["annotation"]["object"])
    if type(parsed["annotation"]["object"]) is list:
        for j in range(num_obj):
            # if parsed["annotation"]["object"][j]["parts"]["hasparts"] is not None:
            #     continue
            if parsed["annotation"]["object"][j]["deleted"] in ["1", 1]:
                continue
            if "assembly" in parsed["annotation"]["object"][j]["name"].lower():
                continue
            if "camera" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            elif "back" not in parsed["annotation"]["object"][j]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            else:
                current_name = parsed["annotation"]["object"][j]["name"].lower()
            obj_idx = unique_objs.index(current_name)
            polygon_coors = extract_poly(parsed["annotation"]["object"][j])
            canvas = Image.fromarray(labels_container[obj_idx])
            ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
            labels_container[obj_idx] = np.array(canvas)

    else:
        if "assembly" not in parsed["annotation"]["object"]["name"].lower() and parsed["annotation"]["object"]["deleted"] not in ["1", 1]:
            # obj_set.add(parsed["annotation"]["object"]["name"].lower())
            if "camera" in parsed["annotation"]["object"]["name"].lower():
                current_name = "camera"
            elif "back" not in parsed["annotation"]["object"]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            else:
                current_name = parsed["annotation"]["object"]["name"].lower()

            print(parsed["annotation"]["object"])
            obj_idx = unique_objs.index(current_name)
            polygon_coors = extract_poly(parsed["annotation"]["object"])
            canvas = Image.fromarray(labels_container[obj_idx])
            ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
            labels_container[obj_idx] = np.array(canvas)
    plt.imshow(np.sum(labels_container, axis=0))
    plt.show()

