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

anno_dir = [r"C:\Users\ALuo\PycharmProjects\CVphone\collection\Annotations\users\tohme\cellphones\samsung_s4_active"]
anno_files = [list(map(lambda x: os.path.join(a,x),os.listdir(a))) for a in anno_dir]
anno_files = sum(anno_files, [])


obj_set = ["motherboard", "battery", "board", "sim holder", "side button",
               "button", "microphone", "speaker", "charging port",
               "motor", "jack", "cover", "back cover", "screen",
               "cable", "camera", "screw", "connector"]

num_unique_objs = len(obj_set)
unique_objs = list(obj_set)
def extract_poly(dict_input):
    points = []
    poly = dict_input["polygon"]["pt"]
    for pt_coor in poly:
        points.append((int(int(pt_coor["x"])*0.2), int(int(pt_coor["y"])*0.2)))
    points.append(points[0])
    return points

for i in range(39, len(anno_files)):
    print("PROCESSING {}".format(i))
    with open(anno_files[i], "rb") as xml_file:
        xml_content = xml_file.read()
    parsed = xmltodict.parse(xml_content)
    y,x = int(int(parsed["annotation"]["imagesize"]["nrows"])*0.2), int(int(parsed["annotation"]["imagesize"]["ncols"])*0.2)
    labels_container = np.zeros((num_unique_objs,y,x))
    other_container = np.zeros((y,x))
    num_obj = len(parsed["annotation"]["object"])
    if type(parsed["annotation"]["object"]) is list:
        for j in range(num_obj):
            # if parsed["annotation"]["object"][j]["parts"]["hasparts"] is not None:
            #     continue
            if parsed["annotation"]["object"][j]["deleted"] in ["1", 1]:
                continue
            # if "assembly" in parsed["annotation"]["object"][j]["name"].lower():
            #     continue
            if "camera" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "camera"
            elif "screw" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "screw"
            elif "back" not in parsed["annotation"]["object"][j]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "cover"
            elif "jack" in parsed["annotation"]["object"][j]["name"].lower() and "assembly" not in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "jack"
            elif "port" in parsed["annotation"]["object"][j]["name"].lower() and "charg" in parsed["annotation"]["object"][j]["name"].lower() and "assembly" not in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "charging port"
            elif "mother" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "motherboard"
            elif "motor" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "motor"
            else:
                current_name = parsed["annotation"]["object"][j]["name"].lower()

            if "frame" not in current_name and "case" not in current_name and "assembly" not in current_name:
                if current_name in obj_set:
                    obj_idx = unique_objs.index(current_name)
                    polygon_coors = extract_poly(parsed["annotation"]["object"][j])
                    canvas = Image.fromarray(labels_container[obj_idx])
                    ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
                    labels_container[obj_idx] = np.array(canvas)
                else:
                    print("INVALID OBJ", current_name)

            elif "frame" in current_name or "case" in current_name or "assembly" in current_name:
                polygon_coors = extract_poly(parsed["annotation"]["object"][j])
                canvas = Image.fromarray(other_container)
                ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
                other_container += np.array(canvas)
    else:
        #if "assembly" not in parsed["annotation"]["object"]["name"].lower() and parsed["annotation"]["object"]["deleted"] not in ["1", 1]:
        if parsed["annotation"]["object"]["deleted"] not in ["1", 1]:
            # obj_set.add(parsed["annotation"]["object"]["name"].lower())
            if "camera" in parsed["annotation"]["object"]["name"].lower():
                current_name = "camera"
            elif "screw" in parsed["annotation"]["object"]["name"].lower():
                current_name = "screw"
            elif "back" not in parsed["annotation"]["object"]["name"].lower() and "cover" in parsed["annotation"]["object"]["name"].lower():
                current_name = "cover"
            elif "jack" in parsed["annotation"]["object"]["name"].lower() and "assembly" not in parsed["annotation"]["object"]["name"].lower():
                current_name = "jack"
            elif "port" in parsed["annotation"]["object"]["name"].lower() and "charg" in parsed["annotation"]["object"]["name"].lower() and "assembly" not in parsed["annotation"]["object"]["name"].lower():
                current_name = "charging port"
            elif "mother" in parsed["annotation"]["object"]["name"].lower():
                current_name = "motherboard"
            elif "motor" in parsed["annotation"]["object"]["name"].lower():
                current_name = "motor"
            else:
                current_name = parsed["annotation"]["object"]["name"].lower()
            # if (current_name not in obj_set) and "frame" not in current_name and "case" not in current_name:
            #     print("INVALID LABEL {}".format(current_name))
            #     continue
            print(parsed["annotation"]["object"])
            if "frame" not in current_name and "case" not in current_name and "assembly" not in current_name:
                if current_name in obj_set:
                    obj_idx = unique_objs.index(current_name)
                    polygon_coors = extract_poly(parsed["annotation"]["object"])
                    canvas = Image.fromarray(labels_container[obj_idx])
                    ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
                    labels_container[obj_idx] = np.array(canvas)
                else:
                    print("INVALID OBJ", current_name)
            elif "frame" in current_name or "case" in current_name or "assembly" in current_name:
                polygon_coors = extract_poly(parsed["annotation"]["object"])
                canvas = Image.fromarray(other_container)
                ImageDraw.Draw(canvas).polygon(polygon_coors, outline=1, fill=1)
                other_container += np.array(canvas)

    outline_labels = np.sum(labels_container, axis= 0)>0.5
    outline_general = other_container>0.5
    general = np.logical_or(outline_labels, outline_general)

    for layer_i in list(range(0, len(labels_container)))[::-1]:
        for layer_j in list(range(0, len(labels_container)))[::-1]:
            if layer_i == layer_j:
                continue
            labels_container[layer_j] = np.logical_and(np.logical_not(labels_container[layer_i]), labels_container[layer_j])
    if np.max(labels_container)<0.5:
        continue
    plt.figure(1)
    plt.subplot(211)
    plt.imshow(np.sum(labels_container, axis=0))
    plt.subplot(212)
    plt.imshow(general)
    plt.show()

















# obj_set = set()
# for i in range(len(anno_files)):
#     with open(anno_files[i], "rb") as xml_file:
#         xml_content = xml_file.read()
#     parsed = xmltodict.parse(xml_content)
#     y,x = int(parsed["annotation"]["imagesize"]["nrows"]), int(parsed["annotation"]["imagesize"]["ncols"])
#     num_obj = len(parsed["annotation"]["object"])
#     if type(parsed["annotation"]["object"]) is list:
#         for j in range(num_obj):
#             if parsed["annotation"]["object"][j]["deleted"] in ["1", 1]:
#                 continue
#             if "assembly" in parsed["annotation"]["object"][j]["name"].lower():
#                 continue
#             current_name = ""
#             if "camera" in parsed["annotation"]["object"][j]["name"].lower():
#                 current_name = "camera"
#             elif "back" not in parsed["annotation"]["object"][j]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
#                 current_name = "camera"
#             else:
#                 current_name = parsed["annotation"]["object"][j]["name"].lower()
#             obj_set.add(current_name)
#     else:
#         if "assembly" not in parsed["annotation"]["object"]["name"].lower() and parsed["annotation"]["object"]["deleted"] not in ["1", 1]:
#             if "camera" in parsed["annotation"]["object"]["name"].lower():
#                 current_name = "camera"
#             elif "back" not in parsed["annotation"]["object"]["name"].lower() and "cover" in parsed["annotation"]["object"][j]["name"].lower():
#                 current_name = "camera"
#             else:
#                 current_name = parsed["annotation"]["object"]["name"].lower()
#             obj_set.add(current_name)
