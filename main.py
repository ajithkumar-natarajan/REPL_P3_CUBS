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

    print("Printing GT")
    print(gt)


img = cv2.imread("22.png")
h, w = img.shape[0:2]
print(img.shape[0:2])
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

for axis, color in [('x', (255, 0, 0)), ('y', (255, 0, 255))]:
  print(axis)
  print(color)
  print("---")

# os.system('python visualize.py 22.json 22.png 22.out.png')

class_to_idx = {'y_axis': {'y_tick_label': 2, 'y_tick_pt': 1, 'y_axis_title': 3, 'background': 0}, 'region': {'plot': 5, 'x_axis': 2, 'background': 0, 'chart_title': 1, 'y_axis': 3, 'legend': 4}, 'legend': {'legend_title': 1, 'legend_label': 2, 'legend_marker': 3, 'background': 0}, 'x_axis': {'x_axis_title': 3, 'background': 0, 'x_tick_pt': 1, 'x_tick_label': 2}, 'plot': {'bars': 2, 'text': 5, 'lines': 3, 'scatter points': 4, 'boxplots': 1, 'background': 0}}

parse_json(img, "22.json", class_to_idx)