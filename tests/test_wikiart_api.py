""" UnitTest """
import os
import unittest
import logging

from wikiartcrawler import WikiartAPI

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')


class Test(unittest.TestCase):
    """ Test ISR model"""

    def test_face_image(self):
        # artist = 'paul-cezanne'
        artist = '*'
        api = WikiartAPI()
        out = api.get_painting(artist, image_type='face')
        print(len(out))
        # api.get_painting_info(artist)

    def test_init(self):
        artist = 'paul-cezanne'
        api = WikiartAPI()
        api.get_painting_info(artist)
        api.get_painting(artist)

    def test_init_credential(self):
        if os.path.exists('./wikiart_credential.json'):
            artist = 'paul-cezanne'
            api = WikiartAPI('./wikiart_credential.json')
            api.get_painting_info(artist)
            api.get_painting(artist)


if __name__ == "__main__":
    unittest.main()
