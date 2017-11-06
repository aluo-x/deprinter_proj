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

anno_dir = [r"C:\Users\ALuo\PycharmProjects\CVphone\collection\Annotations\users\tohme\cellphones\iphone4s"]
anno_files = [list(map(lambda x: os.path.join(a,x),os.listdir(a))) for a in anno_dir]
anno_files = sum(anno_files, [])


obj_set = ["motherboard", "battery", "board", "sim holder", "side button",
               "button", "microphone", "speaker", "charging port",
               "motor", "jack", "cover", "back cover", "screen",
               "cable", "camera", "screw", "connector"]

num_unique_objs = len(obj_set)
unique_objs = list(obj_set)

from scipy.ndimage import zoom

def resize_crop(input_img, new_size = [400, 600], method = 0):
    input_shape = np.shape(input_img)
    height, width = input_shape[0], input_shape[1]
    print(input_shape, new_size)
    zoom_factor = np.max(np.array([float(new_size[0]+1.0)/float(height), float(new_size[1]+1.0)/float(width)]))
    resized_img = zoom(input_img, [zoom_factor, zoom_factor, 1.0], order=method)
    new_size_no_crop = np.shape(resized_img)
    crop_top = int((new_size_no_crop[0]-new_size[0])/2)
    crop_bot = new_size_no_crop[0] - new_size[0] - crop_top

    crop_left = int((new_size_no_crop[1]-new_size[1])/2)
    crop_right = new_size_no_crop[1] - new_size[1] - crop_left
    resized_img = resized_img[crop_top:-crop_bot,crop_left:-crop_right,:]
    return resized_img


scale = 0.2
def extract_poly(dict_input):
    points = []
    poly = dict_input["polygon"]["pt"]
    for pt_coor in poly:
        points.append((int(int(pt_coor["x"])*scale), int(int(pt_coor["y"])*scale)))
    points.append(points[0])
    return points

for i in range(len(anno_files)):
    print("PROCESSING {}".format(i))
    with open(anno_files[i], "rb") as xml_file:
        xml_content = xml_file.read()
    parsed = xmltodict.parse(xml_content)
    y,x = int(int(parsed["annotation"]["imagesize"]["nrows"])*scale), int(int(parsed["annotation"]["imagesize"]["ncols"])*scale)
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
            elif "connector" in parsed["annotation"]["object"][j]["name"].lower():
                current_name = "connector"
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
            elif "connector" in parsed["annotation"]["object"]["name"].lower():
                current_name = "connector"
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
    general = np.logical_and(np.logical_or(outline_general, outline_labels), np.logical_not(outline_labels))
    back_ground = np.logical_and(np.logical_not(general), np.logical_not(outline_labels))

    for layer_i in list(range(0, len(labels_container)))[::-1]:
        for layer_j in list(range(0, len(labels_container)))[::-1]:
            if layer_i == layer_j:
                continue
            labels_container[layer_j] = np.logical_and(np.logical_not(labels_container[layer_i]), labels_container[layer_j])
    if np.max(labels_container)<0.5: #and np.max(outline_general)<0.5:
        continue

    added_arr=np.append(labels_container, np.expand_dims(general, 0),axis=0)
    added_arr=np.append(added_arr, np.expand_dims(back_ground, 0),axis=0)
    added_arr= np.swapaxes(added_arr, 0,2)
    added_arr = np.swapaxes(added_arr, 0,1)
    added_arr = added_arr.astype(np.int8)
    # print(added_arr)
    #np.save(os.path.join(r"C:\Users\ALuo\PycharmProjects\CVphone\annotations", os.path.basename(os.path.dirname(anno_files[i]))) + "_" + os.path.splitext(os.path.basename(anno_files[i]))[0], added_arr)
    # print(np.shape(labels_container), "SHAPE")
    # print("SHAPE", np.shape(added_arr), added_arr.dtype)
    added_arr=resize_crop(added_arr)
    added_arr = added_arr.astype(np.bool)
    if not os.path.isdir(os.path.join(r"C:\Users\ALuo\PycharmProjects\CVphone\annotations", os.path.basename(os.path.dirname(anno_files[i])))):
        os.mkdir(os.path.join(r"C:\Users\ALuo\PycharmProjects\CVphone\annotations", os.path.basename(os.path.dirname(anno_files[i]))))

    np.save(os.path.join(os.path.join(r"C:\Users\ALuo\PycharmProjects\CVphone\annotations", os.path.basename(os.path.dirname(anno_files[i]))),
            os.path.splitext(os.path.basename(anno_files[i]))[0]), added_arr)
    # plt.figure(1)
    # plt.subplot(411)
    # plt.imshow(np.sum(added_arr[:, :, 0:-2], axis=2))
    # plt.subplot(412)
    # plt.imshow(added_arr[:, :, -2])
    # plt.subplot(413)
    # plt.imshow(added_arr[:, :, -1])
    # plt.subplot(414)
    # plt.imshow(np.sum(added_arr, axis=2))
    # plt.show()

















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
