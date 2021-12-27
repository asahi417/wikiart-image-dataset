import os
from typing import List
from glob import glob
from .wikiart_api import CACHE_DIR

__root = os.path.dirname(os.path.abspath(__file__))

VALID_ARTIST_GROUPS = [
    'abstract-expressionism', 'baroque', 'ecole-de-paris', 'expressionism',
    'impressionism', 'naive-art-primitivism', 'neo-impressionism', 'neoclassicism', 'post-impressionism',
    'pre-raphaelite-brotherhood', 'realism', 'rococo', 'romanticism', 'surrealism', 'symbolism'
]


def available_artist(cache_dir: str = None):
    cache_dir = CACHE_DIR if cache_dir is None else cache_dir
    return sorted([os.path.basename(i).replace('.json', '') for i in glob('{}/painting/meta/*.json'.format(cache_dir))])


def get_artist(groups: List or str, cache_dir: str = None):
    if type(groups) is str:
        groups = [groups]
    _artist = available_artist(cache_dir)
    full_artist = []
    for g in groups:
        full_artist += list(filter(lambda x: x in _artist, load_txt(g+'.txt')))
    return sorted(list(set(full_artist)))


def load_txt(_file):
    path = '{}/groups/{}'.format(__root, _file)
    assert os.path.exists(path), _file
    with open(path) as f:
        return sorted(list(set([i for i in f.read().split('\n') if len(i) > 0])))


expressionism = load_txt('expressionism.txt')
impressionism = load_txt('impressionism.txt')
neo_impressionism = load_txt('neo-impressionism.txt')
post_impressionism = load_txt('post-impressionism.txt')
pre_raphaelite_brotherhood = load_txt('pre-raphaelite-brotherhood.txt')
romanticism = load_txt('romanticism.txt')
surrealism = load_txt('surrealism.txt')
symbolism = load_txt('symbolism.txt')
abstract_expressionism = load_txt('abstract-expressionism.txt')
baroque = load_txt('baroque.txt')
ecole_de_paris = load_txt('ecole-de-paris.txt')
naive_art_primitivism = load_txt('naive-art-primitivism.txt')
neoclassicism = load_txt('neoclassicism.txt')
realism = load_txt('realism.txt')
rococo = load_txt('rococo.txt')
