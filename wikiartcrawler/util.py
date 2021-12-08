import os
import tarfile
import zipfile
import gzip
import requests

import gdown


__all__ = 'wget'

URL_LIST = {
    'abstract_expressionism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/abstract_expressionism.zip',
    'baroque': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/abstract_expressionism.zip',
    'ecole_de_paris': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/ecole_de_paris.zip',
    'expressionism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/expressionism.zip',
    'impressionism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/impressionism.zip',
    'naive_art_primitivism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/naive_art_primitivism.zip',
    'neo_impressionism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/neo_impressionism.zip',
    'post_impressionism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/post_impressionism.zip',
    'pre_raphaelite_brotherhood': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/pre_raphaelite_brotherhood.zip',
    'realism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/realism.zip',
    'rococo': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/rococo.zip',
    'romanticism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/romanticism.zip',
    'surrealism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/surrealism.zip',
    'symbolism': 'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/symbolism.zip'
 }


def new_file_path(path, suffix, export_dir: str = None):
    tmp = path.split('.')
    _id = tmp[-1]
    path = '.'.join(tmp[:-1])
    if export_dir is not None:
        path = '{}/{}'.format(export_dir, os.path.basename(path))
    path = '{}.{}.{}'.format(path, suffix, _id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def wget(url, cache_dir: str, gdrive_filename: str = None):
    """ wget and uncompress data_iterator """
    path = _wget(url, cache_dir, gdrive_filename=gdrive_filename)
    if path.endswith('.tar.gz') or path.endswith('.tgz') or path.endswith('.tar'):
        if path.endswith('.tar'):
            tar = tarfile.open(path)
        else:
            tar = tarfile.open(path, "r:gz")
        tar.extractall(cache_dir)
        tar.close()
        os.remove(path)
    elif path.endswith('.gz'):
        with gzip.open(path, 'rb') as f:
            with open(path.replace('.gz', ''), 'wb') as f_write:
                f_write.write(f.read())
        os.remove(path)
    elif path.endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(cache_dir)
        os.remove(path)


def _wget(url: str, cache_dir, gdrive_filename: str = None):
    """ get data from web """
    os.makedirs(cache_dir, exist_ok=True)
    if url.startswith('https://drive.google.com'):
        assert gdrive_filename is not None, 'please provide fileaname for gdrive download'
        return gdown.download(url, '{}/{}'.format(cache_dir, gdrive_filename), quiet=False)
    filename = os.path.basename(url)
    with open('{}/{}'.format(cache_dir, filename), "wb") as f:
        r = requests.get(url)
        f.write(r.content)
    return '{}/{}'.format(cache_dir, filename)

