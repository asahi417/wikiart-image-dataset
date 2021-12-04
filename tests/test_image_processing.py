""" UnitTest """
import unittest
import logging
import shutil
from glob import glob
from wikiartcrawler import portrait_data_pipeline

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

source_images = glob('./tests/test_images/*.jpg')
shutil.rmtree('tests/test_images_processed')


class Test(unittest.TestCase):
    """ Test ISR model"""

    def test(self):
        out = portrait_data_pipeline(source_images, export_dir='tests/test_images_processed', debug_mode=True)
        print(out)


if __name__ == "__main__":
    unittest.main()
