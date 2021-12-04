import os
import tarfile
import zipfile
import gzip
import requests

import gdown


__all__ = 'wget'


def new_file_path(path, suffix, export_dir: str = None):
    tmp = path.split('.')
    _id = tmp[-1]
    path = '.'.join(tmp[:-1])
    if export_dir is not None:
        path = '{}/{}'.format(export_dir, os.path.basename(path))
    path = '{}.{}.{}'.format(path, suffix, _id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # if no_overwrite:
    #     n = 1
    #     while True:
    #         if not os.path.exists(path):
    #             break
    #         _id = path.split('.')[-1]
    #         path = path.replace(_id, '{}.{}'.format(n, _id))
    #         n += 1
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

