import os
import cv2
import numpy as np
import json


def get_bbox(x0, y0, h, w, img_h, img_w):
    xmin = float(x0)
    ymin = float(y0)
    xmax = xmin + float(w)
    ymax = ymin + float(h)

    bbox = np.asarray([xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax])
    bbox = bbox / ([img_w * 1.0, img_h * 1.0] * 4)
    bbox = np.clip(bbox, 0.0, 1.0)
    return bbox



def parse_json(img, gt_path, class_to_idx):
    h, w = img.shape[0:2]

    with open(gt_path, 'r') as f:
        gt_json = json.load(f)

    chart_type_json = gt_json['task1']['output']['chart_type']
    text_blocks_json = gt_json['task3']['input']['task2_output']['text_blocks'] 
    text_roles_json = gt_json['task3']['output']['text_roles']
    plot_bb_json = gt_json['task4']['output']['_plot_bb']
    axes_json = gt_json['task4']['output']['axes']
    legend_markers_json = gt_json['task5']['output']['legend_pairs']
    # visual_elements_json = gt_json['task6']['output']['visual elements']

    gt = {"region":{"bboxes" : [],
                    "roles" : []
                   },
          "legend":{"bboxes" : [],
                    "roles" : []
                   },
          "plot":{"bboxes" : [],
                  "roles":[]
                 },
          "x_axis":{"bboxes" : [],
                    "roles" : []
                   },
          "y_axis":{"bboxes" : [],
                    "roles" : []
                   }          
        }

    for tick in axes_json['x-axis']:
        tick_pt_x = tick['tick_pt']['x']
        tick_pt_y = tick['tick_pt']['y']
        bbox = get_bbox(tick_pt_x-5, tick_pt_y, 10, 10, h, w)
        gt["x_axis"]["bboxes"].append(bbox)
        gt["x_axis"]["roles"].append(class_to_idx["x_axis"]["x_tick_pt"])
    for tick in axes_json['y-axis']:
        tick_pt_x = tick['tick_pt']['x']
        tick_pt_y = tick['tick_pt']['y']
        bbox = get_bbox(tick_pt_x-5, tick_pt_y-5, 10, 10, h, w)
        gt["y_axis"]["bboxes"].append(bbox)
        gt["y_axis"]["roles"].append(class_to_idx["y_axis"]["y_tick_pt"])

    # Text Roles
    # print len(text_roles_json), len(text_blocks_json), gt_path
    text_roles = [None]*len(text_roles_json)
    for text_role in text_roles_json:
        bbox_id = int(text_role['id'])
        try:
            text_roles[bbox_id] = text_role['role']
        except:
            print('********** ' + str(bbox_id) + ', ' + text_role['role']  + ', ' + gt_path)

    # Text Boxes
    text_bboxes = [None]*len(text_blocks_json)
    for text_block in text_blocks_json:
        bbox_id = int(text_block['id'])
        bbox = text_block['bb']
        bbox = get_bbox(bbox['x0'], bbox['y0'], bbox['height'], bbox['width'], h, w)
        text_bboxes[bbox_id] = bbox

    for bbox_id, (role, bbox) in enumerate(zip(text_roles, text_bboxes)):
        if role == 'chart_title':
            gt["region"]["roles"].append(class_to_idx["region"][role])
            gt["region"]["bboxes"].append(bbox)
        elif role in ('legend_title', 'legend_label'):
            gt["legend"]["roles"].append(class_to_idx["legend"][role])
            gt["legend"]["bboxes"].append(bbox)
        elif role in ('x_tick_label', 'x_axis_title'):
            gt["x_axis"]["roles"].append(class_to_idx["x_axis"][role])
            gt["x_axis"]["bboxes"].append(bbox)
        elif role in ('y_tick_label', 'y_axis_title'):
            gt["y_axis"]["roles"].append(class_to_idx["y_axis"][role])
            gt["y_axis"]["bboxes"].append(bbox)
        else:
            gt["plot"]["roles"].append(class_to_idx["plot"]["text"])
            gt["plot"]["bboxes"].append(bbox)

    # Legend Markers
    for legend_marker in legend_markers_json:
        bbox = legend_marker['bb']
        bbox = get_bbox(bbox['x0'], bbox['y0'], bbox['height'], bbox['width'], h, w)
        gt["legend"]["bboxes"].append(bbox)
        gt["legend"]["roles"].append(class_to_idx["legend"]['legend_marker'])

    gt["legend"]["bboxes"] = np.array(gt["legend"]["bboxes"])
    gt["x_axis"]["bboxes"] = np.array(gt["x_axis"]["bboxes"])
    gt["y_axis"]["bboxes"] = np.array(gt["y_axis"]["bboxes"])

    print("Printing GT")
    print(gt)
    # print("plot_bb_json")
    # print(plot_bb_json)


img = cv2.imread("22.png")
h, w = img.shape[0:2]
# print(img.shape[0:2])
# print(type(h))
# print(type(w))


# for i in range(57, 57+101):
#   # for j in range(58, 58+14):
#     img[772][i] = 0

# for i in range(57, 57+101):
#   # for j in range(58, 58+14):
#     img[786][i] = 0

# img[173][777] = 128

# cv2.imwrite("img.png", img)

# for axis, color in [('x', (255, 0, 0)), ('y', (255, 0, 255))]:
#   print(axis)
#   print(color)
#   print("---")

os.system('python visualize.py 22.json 22.png 22.out.png')

class_to_idx = {'y_axis': {'y_tick_label': 2, 'y_tick_pt': 1, 'y_axis_title': 3, 'background': 0}, 'region': {'plot': 5, 'x_axis': 2, 'background': 0, 'chart_title': 1, 'y_axis': 3, 'legend': 4}, 'legend': {'legend_title': 1, 'legend_label': 2, 'legend_marker': 3, 'background': 0}, 'x_axis': {'x_axis_title': 3, 'background': 0, 'x_tick_pt': 1, 'x_tick_label': 2}, 'plot': {'bars': 2, 'text': 5, 'lines': 3, 'scatter points': 4, 'boxplots': 1, 'background': 0}}

parse_json(img, "22.json", class_to_idx)