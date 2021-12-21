import os
import logging
from tqdm import tqdm

import cv2
from PIL import Image

from wikiartcrawler import WikiartAPI, image_processors


logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
api = WikiartAPI()
export_dir = './data/image_face_blur'


logging.info('***BLUR IMAGE***')

logging.info('Step 1: fetch image')
image_path = []
for i in tqdm(api.artist_wikiart):
    tmp_image_files = api.get_painting(i, image_type='face')
    if tmp_image_files is not None:
        image_path += tmp_image_files
logging.info('total face images: {}'.format(len(image_path)))

logging.info('Step 2: blur image')
for i in tqdm(image_path):
    artist_name, img_name = i.split('/')[-2:]
    img = cv2.cvtColor(cv2.imread(i), cv2.COLOR_BGR2RGB)
    img = image_processors.blur_image(img)
    file_path = '{}/{}/{}'.format(export_dir, artist_name, img_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    Image.fromarray(img).save(file_path)

logging.info('dataset is ready at {}'.format(export_dir))
