import os
import gc
import logging
from tqdm import tqdm
from wikiartcrawler import WikiartAPI, get_face_image, ISRModel

CREDENTIAL = os.getenv('CREDENTIAL', None)  # 'wikiart_credential.json'
SKIP_DOWNLOAD = bool(int(os.getenv('SKIP_DOWNLOAD', 1)))

export_dir = './data/image_face'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

logging.info('***GENERATE PORTRAIT DATASET***')

logging.info('Step 1: fetch images from wikiart')
api = WikiartAPI(CREDENTIAL, skip_download=SKIP_DOWNLOAD)

image_path = []
for i in tqdm(api.artist_wikiart):
    tmp_image_files = api.get_painting(i)
    if tmp_image_files is not None:
        image_path += tmp_image_files

logging.info('total {} images'.format(len(image_path)))


logging.info('Step 2: process for portrait dataset')
non_portrait_images = '{}/non_portrait_images.txt'.format(export_dir)
if os.path.exists(non_portrait_images):
    with open(non_portrait_images) as f:
        non_portrait_images_files = f.read().split('\n')
else:
    non_portrait_images_files = []


def get_export_path(_path):
    artist = os.path.basename(os.path.dirname(_path))
    img_name = os.path.basename(_path)
    return '{}/{}/{}'.format(export_dir, artist, img_name)


isr_model = ISRModel('noise-cancel')
with open(non_portrait_images, 'w') as f:
    f.write('\n'.join(non_portrait_images_files) + '\n')
    for i in tqdm(image_path):
        basename = '/'.join(i.split('/')[-2:])
        if basename in non_portrait_images_files:
            continue
        e = get_export_path(i)
        if os.path.exists(e):
            continue
        _e = get_face_image(i, export_path=e, isr_model=isr_model)
        if _e is None:
            f.write('{}\n'.format(basename))
        gc.collect()

logging.info('dataset is ready at {}'.format(export_dir))
