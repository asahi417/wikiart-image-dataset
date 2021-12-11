""" Image Super Resolution. """
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
    """ Image Super Resolution. """

    def __init__(self, model: str = 'noise-cancel'):
        """ Image Super Resolution.

        :param model: ISR model ('noise-cancel', 'psnr-small', 'psnr-large', 'gans')
        """
        self.model = get_isr_model(model)

    def predict(self,
                image_path: str,
                export_path: str = None,
                suffix: str = 'isr',
                export_dir: str = None):
        """ Predict super-resolution image.

        :param image_path: Path to an image.
        :param export_path: Path to save the model predicted ISR image.
        :param suffix: Alternative to give the export_path, specify a suffix to the original image path for export_path.
        :param export_dir: Directory to export when use suffix to create export_path.
        :return: Path to the exported image.
        """
        if export_path is None:
            export_path = new_file_path(image_path, suffix, export_dir)
        else:
            assert type(export_path) is str, export_path
        out = self.process_single_image(image_path)
        Image.fromarray(out).save(export_path)
        return export_path

    def process_single_image(self, image_path):
        img = Image.open(image_path)
        lr_img = np.array(img)
        sr_img = self.model.predict(lr_img)
        return sr_img

