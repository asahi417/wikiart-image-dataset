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


def load_artists(group_name):
    if group_name == 'abstract-expressionism':
        from .groups.abstract_expressionism import groups
    elif group_name == 'baroque':
        from .groups.baroque import groups
    elif group_name == 'ecole-de-paris':
        from .groups.ecole_de_paris import groups
    elif group_name == 'expressionism':
        from .groups.expressionism import groups
    elif group_name == 'impressionism':
        from .groups.impressionism import groups
    elif group_name == 'naive-art-primitivism':
        from .groups.naive_art_primitivism import groups
    elif group_name == 'neo-impressionism':
        from .groups.neo_impressionism import groups
    elif group_name == 'neoclassicism':
        from .groups.neoclassicism import groups
    elif group_name == 'post-impressionism':
        from .groups.post_impressionism import groups
    elif group_name == 'pre-raphaelite-brotherhood':
        from .groups.pre_raphaelite_brotherhood import groups
    elif group_name == 'realism':
        from .groups.realism import groups
    elif group_name == 'rococo':
        from .groups.rococo import groups
    elif group_name == 'romanticism':
        from .groups.romanticism import groups
    elif group_name == 'surrealism':
        from .groups.surrealism import groups
    elif group_name == 'symbolism':
        from .groups.symbolism import groups
    else:
        raise ValueError('unknown group: {}'.format(group_name))
    return groups


def available_artist(cache_dir: str = None):
    cache_dir = CACHE_DIR if cache_dir is None else cache_dir
    return sorted([os.path.basename(i).replace('.json', '') for i in glob('{}/painting/meta/*.json'.format(cache_dir))])


def get_artist(groups: List or str, cache_dir: str = None):
    if type(groups) is str:
        groups = [groups]
    _artist = available_artist(cache_dir)
    full_artist = []
    for g in groups:
        print(_artist)
        print(g)
        full_artist += list(filter(lambda x: x in _artist, load_artists(g)))
    return sorted(list(set(full_artist)))


# def load_txt(_file):
#     path = '{}/groups/{}'.format(__root, _file)
#     assert os.path.exists(path), _file
#     with open(path) as f:
#         return sorted(list(set([i for i in f.read().split('\n') if len(i) > 0])))


expressionism = load_artists('expressionism')
impressionism = load_artists('impressionism')
neo_impressionism = load_artists('neo-impressionism')
post_impressionism = load_artists('post-impressionism')
pre_raphaelite_brotherhood = load_artists('pre-raphaelite-brotherhood')
romanticism = load_artists('romanticism')
surrealism = load_artists('surrealism')
symbolism = load_artists('symbolism')
abstract_expressionism = load_artists('abstract-expressionism')
baroque = load_artists('baroque')
ecole_de_paris = load_artists('ecole-de-paris')
naive_art_primitivism = load_artists('naive-art-primitivism')
neoclassicism = load_artists('neoclassicism')
realism = load_artists('realism')
rococo = load_artists('rococo')
