import logging
from wikiartcrawler import WikiartAPI

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
WikiartAPI(skip_download=True)
