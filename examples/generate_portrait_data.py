import logging
from tqdm import tqdm
from wikiartcrawler import WikiartAPI, portrait_data_pipeline


export_dir = './data/portrait'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

logging.info('***GENERATE PORTRAIT DATASET***')

logging.info('Step 1: fetch images from wikiart')
# wikiart_credential = 'wikiart_credential.json'
# api = WikiartAPI(wikiart_credential)
api = WikiartAPI()
image_path = []
for i in tqdm(api.artist_wikiart):
    tmp_image_files = api.get_painting(i)
    image_path += tmp_image_files

logging.info('total {} images'.format(len(image_path)))

logging.info('Step 2: process for portrait dataset')
processed_files = portrait_data_pipeline(image_path, export_dir=export_dir)
logging.info('total {} images'.format(len(processed_files)))
logging.info('dataset is ready at {}'.format(export_dir))
