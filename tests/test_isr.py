""" UnitTest """
import unittest
import logging
import shutil
from glob import glob

from wikiartcrawler import ISRModel

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

source_images = glob('./tests/test_images/*.jpg')
shutil.rmtree('tests/test_images_isr')


class Test(unittest.TestCase):
    """ Test ISR model"""

    def test_model(self):
        model = ISRModel()
        model.predict(source_images, export_dir='tests/test_images_isr')


if __name__ == "__main__":
    unittest.main()
