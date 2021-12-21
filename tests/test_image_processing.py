""" UnitTest """
import unittest
import logging
import shutil
from glob import glob
from wikiartcrawler import get_face_image

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

source_images = glob('./tests/test_images/*.jpg')
shutil.rmtree('tests/test_images_processed')


class Test(unittest.TestCase):
    """ Test ISR model"""

    def test(self):
        out = get_face_image(source_images, export_dir='tests/test_images_processed', debug_mode=True)
        print(out)


if __name__ == "__main__":
    unittest.main()
