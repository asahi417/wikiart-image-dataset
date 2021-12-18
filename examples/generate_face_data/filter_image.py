import shutil
import os
import logging
from tqdm import tqdm
from glob import glob

from wikiartcrawler.image_processors import get_face_landmark


export_dir = './data/image_face'
export_dir_removed = './data/image_face_removed'
os.makedirs(export_dir_removed, exist_ok=True)

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

# statistics
images = sorted(glob('{}/*/*.jpg'.format(export_dir)))
logging.info('total image: {}'.format(len(images)))

# filter
invalid_image = []
for i in tqdm(images):
    angle = get_face_landmark(i)
    if angle is None:
        invalid_image.append(i)
        artist, name = i.split('/')[-2:]
        shutil.move(i, '{}/{}.{}'.format(export_dir_removed, artist, name))
logging.info('total invalid images: {}'.format(len(invalid_image)))

# clean-up directory
for i in glob('{}/*'.format(export_dir)):
    if not os.path.isdir(i):
        continue
    if len(glob('{}/*'.format(i))) == 0:
        shutil.rmtree(i)

# statistics
logging.info('total artist: {}'.format(len(glob('{}/*'.format(export_dir)))))
logging.info('total image : {}'.format(len(glob('{}/*/*.jpg'.format(export_dir)))))
