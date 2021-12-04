""" UnitTest """
from glob import glob
import unittest
import logging

from wikiartcrawler import ISRModel

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

source_images = glob('./tests/test_images/*.jpg')


class Test(unittest.TestCase):
    """ Test ISR model"""

    def test_model(self):
        model = ISRModel()
        model.predict(source_images)


if __name__ == "__main__":
    unittest.main()
