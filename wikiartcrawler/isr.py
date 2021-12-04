import logging
from tqdm import tqdm
import numpy as np
from ISR.models import RRDN, RDN
from PIL import Image

from .util import new_file_path


def get_isr_model(model_name):
    assert model_name in ['noise-cancel', 'psnr-small', 'psnr-large', 'gans']
    if model_name in ['noise-cancel', 'psnr-small', 'psnr-large']:
        return RDN(weights=model_name)
    return RRDN(weights=model_name)


class ISRModel:

    def __init__(self, model: str = 'noise-cancel'):
        self.model = get_isr_model(model)

    def predict(self,
                image_path,
                export_path=None,
                suffix: str = 'isr',
                export_dir: str = './isr_output'):
        if type(image_path) is str:
            if export_path is None:
                export_path = new_file_path(image_path, suffix, export_dir)
            else:
                assert type(export_path) is str, export_path
            out = self.process_single_image(image_path)
            Image.fromarray(out).save(export_path)
            return export_path
        else:
            export_files = []
            assert type(image_path) is list and all(type(i) is str for i in image_path), image_path
            if export_path is None:
                export_path = [new_file_path(i, suffix, export_dir) for i in image_path]
            else:
                assert type(export_path) is list and all(type(i) is str for i in export_path), export_path
                assert len(export_path) == len(image_path)
            logging.info('ISR model:  process {} images'.format(len(image_path)))
            for _i, _e in tqdm(zip(image_path, export_path)):
                out = self.process_single_image(_i)
                Image.fromarray(out).save(_e)
                export_files.append(_e)
            return export_files

    def process_single_image(self, image_path):
        img = Image.open(image_path)
        lr_img = np.array(img)
        sr_img = self.model.predict(lr_img)
        return sr_img

