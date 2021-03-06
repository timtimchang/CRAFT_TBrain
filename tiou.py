pip install -q https://storage.googleapis.com/stt-data-storage/tiou_metric-0.1.0-py2.py3-none-any.whl
import cv2
import os
import numpy as np
from tiou_metric.ic15 import tiou

# valid dataset
with open('/content/Character-Region-Awareness-for-Text-Detection-/source/data/valid_pairs_v2.txt') as f:
  lines = f.readlines()

from shutil import copyfile

dst_dir = 'valid_images'
os.mkdir(dst_dir)
os.mkdir(dst_dir+'/img/')
os.mkdir(dst_dir+'/json/')

for line in lines:
  idx, img_src, json_src = line.split("\t")
  json_src = json_src.split("\n")[0]
  
  img_dst = dst_dir + img_src.split('TrainDataset')[1]
  json_dst = dst_dir + json_src.split('TrainDataset')[1]

  copyfile(img_src, img_dst)
  copyfile(json_src, json_dst)

# test craft
result_file = 'result_0e49'
for text_threshold in [0.7]:
    for low_text in [0.4]:
        for link_threshold in [0.2]:
            print(f'{text_threshold}/{low_text}/{link_threshold}')
            cmd = f'python test.py --trained_model=/content/Character-Region-Awareness-for-Text-Detection-/source/vgg_ICDAR_0e_49.810.pkl --test_folder=/content/valid_images/img --text_threshold {text_threshold} --low_text {low_text} --link_threshold {link_threshold}'
            os.system(cmd)
            os.rename('result', f'{result_file}-{text_threshold}-{low_text}-{link_threshold}')

# tiou
import glob
import json

import numpy as np
import imgproc

def output_result_img(img_path, tures, preds, output_path):
    img = imgproc.loadImage(img_path)
    img = np.array(img)
    for ture_poly in tures:
        poly = np.array(ture_poly)
        cv2.polylines(img, [poly.reshape((-1, 1, 2))], True, 
                      color=(0, 0, 255), thickness=2)
    for pred_poly in preds:
        poly = np.array(pred_poly)
        cv2.polylines(img, [poly.reshape((-1, 1, 2))], True, 
                      color=(0, 255, 0), thickness=2)
    cv2.imwrite(output_path, img)


tures_dict = {}

for dir in glob.glob(result_file + '-*/'):
    tures_list = []
    preds_list = []
    nums = []
    for txt_path in glob.glob(dir + '/*.txt'):
        num = txt_path.split('_')[-1].split('.')[0]
        if num not in tures_dict:
            true_json = json.load(open(f'/content//TrainDataset/json/img_{num}.json'))
            tures = []
            for s in true_json['shapes']:
                points = s['points']
                ture = points[0] + points[1] + points[2] + points[3]
                ture = [int(x) for x in ture]
                tures.append(ture)
            tures_dict[num] = list(tures)
        else:
            tures = list(tures_dict[num])

        # predictions
        preds = []
        for line in open(txt_path).readlines():
            points = [int(p) for p in line.strip().split(',')]
            if len(points) == 8:
                preds.append(points)
            else:
                assert False
                cnt = np.array(points)
                cnt.resize((-1, 2))
                rect = cv2.minAreaRect(cnt)
                boxes = cv2.boxPoints(rect).tolist()
                pred = boxes[0] + boxes[1] + boxes[2] + boxes[3]
                pred = [int(p) for p in pred]
                preds.append(pred)

        # output result images
        # img_path = f'../TrainDataset/img/img_{num}.jpg'
        # output_path = f'{dir}/res_img_{num}.jpg'
        # output_result_img(img_path, tures, preds, output_path)

        tures_list.append(tures)
        preds_list.append(preds)
        nums.append(num)

    
    results = tiou.evaluate_method(tures_list, preds_list, tiou.default_evaluation_params())['per_sample']

    tiou_precisions, tiou_recalls, tiou_f1s = [], [], []
    for _, result in results.items():
        tiou_precisions.append(result['tiouPrecision'])
        tiou_recalls.append(result['tiouRecall'])
        tiou_f1s.append(result['iouHmean'])

    avg_precsion = np.mean(tiou_precisions)
    avg_recall = np.mean(tiou_recalls)
    avg_f1 = np.mean(tiou_f1s)
    print(f'=== {dir}: {avg_precsion}/{avg_recall}/{avg_f1}')
