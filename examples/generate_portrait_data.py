import os
import logging
from tqdm import tqdm
from wikiartcrawler import WikiartAPI, portrait_data_pipeline

CREDENTIAL = os.getenv('CREDENTIAL', None)  # 'wikiart_credential.json'
SKIP_DOWNLOAD = bool(int(os.getenv('SKIP_DOWNLOAD', 1)))
print(CREDENTIAL)
print(SKIP_DOWNLOAD)

export_dir = './data/portrait'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

logging.info('***GENERATE PORTRAIT DATASET***')

logging.info('Step 1: fetch images from wikiart')
api = WikiartAPI(CREDENTIAL, skip_download=SKIP_DOWNLOAD)

image_path = []
for i in tqdm(api.artist_wikiart):
    tmp_image_files = api.get_painting(i)
    if tmp_image_files is not None:
        image_path += tmp_image_files

logging.info('total {} images'.format(len(image_path)))


def get_export_path(_path):
    artist = os.path.basename(os.path.dirname(_path))
    img_name = os.path.basename(_path)
    return '{}/{}/{}'.format(export_dir, artist, img_name)

export_path = [get_export_path(i) for i in image_path]


logging.info('Step 2: process for portrait dataset')
processed_files = portrait_data_pipeline(image_path, export_path=export_path)
logging.info('total {} images'.format(len(processed_files)))
logging.info('dataset is ready at {}'.format(export_dir))
