import numpy as np
import os
import cv2
from core.frontend import YOLO
import json
from collections import defaultdict
def main(eval_folder='./imaged_tryout', online_prediction=False):


    labels = ["apple", "banana", "broccoli", "burger", "cookie", "egg", "frenchfry", "hotdog", "pasta", "pizza", "rice", "salad", "strawberry", "tomato"]


    label_file = os.path.join(eval_folder,'label.txt')
    prediction_file = os.path.join(eval_folder, 'prediction.txt')

    if os.path.exists(label_file) is False:
        raise FileNotFoundError()

    with open(label_file) as f:
        lines = f.read().splitlines()
        ground_truth_dict = { line.split(' ')[0]:line.split(' ')[1:] for line in lines }

    if online_prediction:
        training_result_folder = '/home/xiao/video_project/YOLOv2/traning_results/YOLOv2_meal_6'
        config_path = os.path.join(training_result_folder, 'config.json')
        with open(config_path) as config_buffer:
            config = json.load(config_buffer)
        yolo = YOLO.init_from_config(config)
        results_dict = dict()
        for k, v in ground_truth_dict.items():
            img = cv2.imread(os.path.join(eval_folder,k))
            # get predictions
            boxes = yolo.predict(img, obj_threshold=0.1, nms_threshold=0.3)
            # filter
            predictions = filter_prediction(boxes, 0.5)
            # transform output to labels
            predictions = [labels[prediction.get_label()] for prediction in predictions]
            results_dict[k] = predictions

    else:
        with open(prediction_file) as f:
            lines = f.read().splitlines()
            results_dict = { line.split(' ')[0]:line.split(' ')[1:] for line in lines }

    #compute recogntion rate = 0.5 * (detection rate + rejection rate)
    tp_dict = defaultdict(int)

    fp_dict = defaultdict(int)

    for k, v in ground_truth_dict.items():
        # compute detection rate
        #for every l1 in ground_truth labels
        for l1 in v:
            #l successfully detected
            if l1 in results_dict[k]:
                tp_dict[l1] = tp_dict[l1] + 1

            # # l not detected
            # else:
            #     fn_dict[l1] = fn_dict[l1] + 1

        # compute rejection rate
        # for every l2 in predictions
        for l2 in results_dict[k]:
            if l2 in v:
                pass

            # l2 miss fire
            else:
                fp_dict[l2] = fp_dict[l2] + 1

    for cls, tp in tp_dict.items():
        # compute detection rate
        p_images = len([ k for k, v in ground_truth_dict.items() if cls in v ])
        detection_rate = tp * 1.0 / p_images

        n_images = len(ground_truth_dict.items()) - p_images
        rejection_rate = 1 - fp_dict[cls] * 1.0 / n_images
        print('%s : detection rate: %.2f, reject rate: % 0.2f, recogntion rate %.2f '
              % (cls,detection_rate,rejection_rate,(detection_rate+rejection_rate)/2.))


def filter_prediction(boxes, sub_threshold = 0.5):

    boxes = sorted(boxes, key=lambda box: box.get_score(),reverse=True)

    predictions = [ boxes[0] ]

    for i in range(len(boxes)):
        box = boxes[i]
        if box.get_score() > sub_threshold:
            predictions.append(box)

    return predictions

if __name__ == '__main__':
    main()