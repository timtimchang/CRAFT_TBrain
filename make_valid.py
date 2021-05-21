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
