"""
Default request Limits
API calls: 10 requests per 2.5 seconds
Images downloading: 20 requests per second
Max requests per hour: 400
Max IPs per hour: 10
"""

import os
import shutil

import requests
import logging
import json
from glob import glob
from string import ascii_lowercase
from itertools import permutations
from typing import List
from tqdm import tqdm

from .util import wget, URL_LIST

CACHE_DIR = f"{os.path.expanduser('~')}/.cache/wikiartcrawler"
os.makedirs(CACHE_DIR, exist_ok=True)
CUSTOM_ARTISTS = {
    'francis-bacon': '57726d7fedc2cb3880b4812f',
    'paul-cezanne': '57726d84edc2cb3880b48a5b',
    'vincent-van-gogh': '57726d82edc2cb3880b486a0',
    'pablo-picasso': '57726d84edc2cb3880b48c4d',
    'juan-gris': '57726d82edc2cb3880b48710',
    'georges-braque': '57726d7fedc2cb3880b480b4',
    'alberto-giacometti': '57726d87edc2cb3880b49265'
}
__all__ = 'WikiartAPI'


def api_request(url, session_key: str = None, ignore_error: bool = False):

    def validate_response(_response):
        try:
            _data = _response.json()
        except json.decoder.JSONDecodeError:
            if not ignore_error:
                raise ValueError(f'JSONDecodeError: {str(_response)}')
            logging.warning(f'JSONDecodeError: {str(_response)}')
            return None
        if _response.status_code != 200:
            if not ignore_error:
                raise ValueError(f'API error\n\t url: {url}\n\t error: {_data}')
            logging.warning(f'API error\n\t url: {url}\n\t error: {_data}')
            return None
        return _data

    if session_key is not None:
        url = f'{url}&authSessionKey={session_key}' if '?' in url else f'{url}?authSessionKey={session_key}'

    response = requests.get(url)
    data = validate_response(response)
    if data is None:
        return None

    if 'data' not in data:
        return data
    full_list = data['data']
    if 'hasMore' not in data:
        return full_list
    while data['hasMore']:
        token = data['paginationToken']
        response = requests.get(
            f'{url}&paginationToken={token}' if '?' in url else f'{url}?paginationToken={token}'
        )
        data = validate_response(response)
        if data is None:
            break
        full_list += data['data']
    return full_list


def get_session_key(access_code: str, secret_code: str):
    data = api_request(
        f'https://www.wikiart.org/en/Api/2/login?accessCode={access_code}&secretCode={secret_code}',
        secret_code,
        ignore_error=True
    )
    if data is None:
        return None
    if 'SessionKey' not in data:
        return None
    return data['SessionKey']


def get_image(url, export_path):
    """Download image from url."""
    img_data = requests.get(url).content
    with open(export_path, 'wb') as handler:
        handler.write(img_data)


def get_painting_detail(paint_id: str = '57e00504edc2ca0d8c0b38a2', session_key: str = None):
    return api_request(f'https://www.wikiart.org/en/api/2/Painting?id={paint_id}', session_key)


class WikiartAPI:

    def __init__(self,
                 credentials_file: str = None,
                 credentials: List = None,
                 access_code: str = None,
                 secret_code: str = None,
                 session_key: List = None,
                 force_refresh_artist_id: bool = False,
                 session_num: int = 10,
                 cache_dir: str = None,
                 skip_download: bool = True):
        self.skip_download = skip_download
        if self.skip_download:
            assert not force_refresh_artist_id
        if not self.skip_download and credentials_file is not None:
            with open(credentials_file) as f:
                credentials = [json.loads(i) for i in f.read().split('\n') if len(i) > 0]
        if not self.skip_download and (access_code and secret_code) or credentials:
            if credentials is None:
                credentials = {"access_code": access_code, "secret_code": secret_code}
            self._session_key = []
            for c in credentials:
                assert "access_code" in c and "secret_code" in c, c
                self._session_key += list(filter(None, [
                    get_session_key(**c) for _ in range(session_num)
                ]))
            self._session_key = None if len(self._session_key) == 0 else self._session_key
        elif session_key is not None:
            self._session_key = session_key
        else:
            self._session_key = None

        if self._session_key is not None:
            logging.info(f'{len(self._session_key)} session keys: {self._session_key}')
        else:
            logging.info('No session keys provided')

        self.cur_session_key_index = 0
        self.cache_dir = CACHE_DIR if cache_dir is None else cache_dir

        self.dict_group = self.get_full_group(force_refresh_artist_id)
        self.dict_artist = self.get_full_artist(force_refresh_artist_id)
        self.download_cached_images(force_refresh_artist_id)

        # artist on wikiart
        self.artist_wikiart = sorted(list(self.dict_artist.keys()))

    @property
    def session_key(self):
        if self._session_key is None:
            return None
        if self.cur_session_key_index == len(self._session_key):
            self.cur_session_key_index = 0
        cur_sk = self._session_key[self.cur_session_key_index]
        self.cur_session_key_index += 1
        return cur_sk

    def download_cached_images(self, force_refresh_artist_id):
        logging.info('downloading cached image (this might take some time)')
        os.makedirs(f'{self.cache_dir}/tmp', exist_ok=True)
        target_dir = f'{self.cache_dir}/painting/meta'
        if not os.path.exists(target_dir) or force_refresh_artist_id:
            os.makedirs(os.path.dirname(target_dir), exist_ok=True)
            wget(
                'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/meta.zip',
                cache_dir=f'{self.cache_dir}/tmp'
            )
            shutil.move(f'{self.cache_dir}/tmp/meta', target_dir)

        target_dir = f'{self.cache_dir}/painting/image'
        if not os.path.exists(target_dir) or force_refresh_artist_id:
            os.makedirs(os.path.dirname(target_dir), exist_ok=True)
            for k, url in URL_LIST.items():
                cache_dir = f'{self.cache_dir}/tmp/{k}'
                if not os.path.exists(cache_dir):
                    wget(url, cache_dir=f'{self.cache_dir}/tmp')
                for d in glob(f'{self.cache_dir}/tmp/{k}/*'):
                    target_dir = f'{self.cache_dir}/painting/image/{os.path.basename(d)}'
                    if os.path.exists(target_dir):
                        shutil.rmtree(d)
                    else:
                        shutil.move(d, os.path.dirname(target_dir))
        n_images = len(glob(f'{self.cache_dir}/painting/image/*/*.jpg'))
        logging.info(f'{n_images} images in total')

        target_dir = f'{self.cache_dir}/painting/image_face'
        if not os.path.exists(target_dir) or force_refresh_artist_id:
            wget(
                'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/image_face.zip',
                cache_dir=f'{self.cache_dir}/tmp'
            )
            shutil.move(f'{self.cache_dir}/tmp/image_face', target_dir)

        target_dir = f'{self.cache_dir}/painting/image_face_blur'
        if not os.path.exists(target_dir) or force_refresh_artist_id:
            wget(
                'https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/image_face_blur.zip',
                cache_dir=f'{self.cache_dir}/tmp'
            )
            shutil.move(f'{self.cache_dir}/tmp/image_face_blur', target_dir)

        if os.path.exists(f'{self.cache_dir}/tmp'):
            shutil.rmtree(f'{self.cache_dir}/tmp')

    def get_full_group(self, force_refresh_artist_id):
        cache_file = f'{self.cache_dir}/dictionaries.json'
        if os.path.exists(cache_file) and not force_refresh_artist_id:
            with open(cache_file) as f:
                return json.load(f)
        if not force_refresh_artist_id:
            wget(
                'https://raw.githubusercontent.com/asahi417/wikiart-crawler/master/assets/dictionaries.json',
                cache_dir=self.cache_dir
            )
            with open(cache_file) as f:
                return json.load(f)
        assert not self.skip_download
        data = api_request('https://www.wikiart.org/en/api/2/UpdatedDictionaries', self.session_key)
        data = {i['title']: {'id': i['id'], 'url': i['url'], 'group': i['group']} for i in data}
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        return data

    def get_full_artist(self, force_refresh_artist_id):
        cache_file = f'{self.cache_dir}/artists.json'
        # logging.warning("This endpoint has an issue and will return partial list only.")
        if os.path.exists(cache_file) and not force_refresh_artist_id:
            with open(cache_file) as f:
                return json.load(f)

        if not force_refresh_artist_id:
            wget(
                'https://raw.githubusercontent.com/asahi417/wikiart-crawler/master/assets/artists.json',
                cache_dir=self.cache_dir
            )
            with open(cache_file) as f:
                return json.load(f)

        # basic request (this returns only partial artists)
        assert not self.skip_download
        data = api_request('https://www.wikiart.org/en/api/2/UpdatedArtists', self.session_key, ignore_error=True)
        data = {i['url']: i['id'] for i in data}
        data.update(CUSTOM_ARTISTS)
        logging.info(f'`UpdatedArtists` returned {len(data)} artists')

        # heuristics to cover more artists
        logging.info('heuristics query to enrich the artist list')
        for a, b in tqdm(list(permutations(ascii_lowercase, 2))):
            _data = api_request(f'https://www.wikiart.org/en/api/2/PaintingSearch?term={a}{b}', self.session_key)
            if _data is None:
                break

            for __data in _data:
                if __data['artistUrl'] not in data:
                    data[__data['artistUrl']] = __data['artistId']
        data = {k: v for k, v in data.items() if k is not None}
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        return data

    def get_painting_info(self,
                          artist_url: str,
                          year_start: int = None,
                          year_end: int = None,
                          media: List = None,
                          genre: List = None,
                          style: List = None,
                          max_aspect_ratio: float = None,
                          min_height: int = None,
                          min_width: int = None):

        assert artist_url in self.dict_artist, f'{artist_url} not found in the artist list'
        artist_id = self.dict_artist[artist_url]
        cache_file = f'{self.cache_dir}/painting/meta/{artist_url}.json'
        if not os.path.exists(cache_file):
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            if self.skip_download:
                return None
            painting_info = api_request(
                f'https://www.wikiart.org/en/api/2/PaintingsByArtist?id={artist_id}',
                self.session_key)
            logging.info(f'requesting detail information of paintings: {artist_url}, artist:{artist_url}')
            for _data in tqdm(painting_info):
                if 'FRAME-600x480' in _data['image']:
                    logging.warning(f'Artworks of {artist_url} are not available in your country on copyright grounds.')
                    return []
                _data['detail'] = get_painting_detail(_data['id'], self.session_key)
            with open(cache_file, 'w') as f:
                json.dump(painting_info, f)
        with open(cache_file) as f:
            painting_info = json.load(f)

        if year_start is not None:
            painting_info = list(
                filter(lambda i: i['completitionYear'] >= year_start if 'completitionYear' in i else False,
                       painting_info))
        if year_end is not None:
            painting_info = list(
                filter(lambda i: i['completitionYear'] <= year_end if 'completitionYear' in i else False,
                       painting_info))
        if style is not None:
            painting_info = list(
                filter(lambda i: any(s in i['detail']['styles'] for s in style) if 'style' in i['detail'] else False,
                       painting_info))
        if media is not None:
            painting_info = list(
                filter(lambda i: any(s in i['detail']['media'] for s in media) if 'media' in i['detail'] else False,
                       painting_info))
        if genre is not None:
            painting_info = list(
                filter(lambda i: any(s in i['detail']['genres'] for s in genre) if 'genres' in i['detail'] else False,
                       painting_info))
        if max_aspect_ratio is not None:
            painting_info = list(filter(
                lambda i: max(i['width'], i['height'])/min(i['width'], i['height']) <= max_aspect_ratio
                if type(i['width']) is int and type(i['height']) is int else False, painting_info))
        if min_height is not None:
            painting_info = list(filter(lambda i: i['height'] >= min_height if 'height' in i else False,
                                        painting_info))
        if min_width is not None:
            painting_info = list(filter(lambda i: i['width'] >= min_width if 'width' in i else False,
                                        painting_info))
        return painting_info

    def get_painting(self,
                     artist_url: str,
                     year_start: int = None,
                     year_end: int = None,
                     media: List = None,
                     genre: List = None,
                     style: List = None,
                     max_aspect_ratio: float = None,
                     min_height: int = None,
                     min_width: int = None,
                     image_type: str = None):
        raw_image = True
        if image_type is not None:
            image_type = f'image_{image_type}'
            raw_image = False
        else:
            image_type = 'image'

        if all(i is None for i in [year_start, year_end, media, genre, style, max_aspect_ratio, min_height, min_width]) \
                and self.skip_download:
            paths = glob(f'{self.cache_dir}/painting/{image_type}/{artist_url}/*.jpg')
            return paths if len(paths) != 0 else None

        painting_info = self.get_painting_info(
            artist_url, year_start, year_end, media, genre, style, max_aspect_ratio, min_height, min_width
        )
        if painting_info is None:
            return None
        logging.info(f'downloading image: {len(painting_info)} images, artist: {artist_url}')
        cache_dir = f'{self.cache_dir}/painting/{image_type}/{artist_url}'
        os.makedirs(cache_dir, exist_ok=True)
        image_files = []
        for data in painting_info:
            if 'FRAME-600x480' in data['image']:
                logging.warning(f'access blocked: {data}')
                continue
            _id = data['image'].split('.')[-1]
            path = f"{cache_dir}/{data['url']}.{_id}"
            if not os.path.exists(path):
                if self.skip_download or not raw_image:
                    logging.info(f'file not found but skip download: {path}')
                    continue
                logging.info(f'file not found, downloading {path}')
                get_image(data['image'], path)
            image_files.append(path)
        return image_files if len(image_files) != 0 else None
