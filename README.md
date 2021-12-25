# WikiART Crawler
<p align="center">
  <img src="assets/wikiart_raw.png" width="400">
</p>

**WikiART Crawler** is a python-library to download/process images from [WikiART](https://www.wikiart.org/) via WikiART API. 
If you are interested in the WikiART image set only, see [dataset section](#dataset-links).

## Get Started
```shell
git clone https://github.com/asahi417/wikiart-crawler
cd wikiart-crawler
pip install .
```

## Basic Usage
The basic usage is to specify a single artist and get the file paths of the artist's image downloaded locally at the first time
(the cache directory is `~/.cache/wikiartcrawler` as default).
```python
from wikiartcrawler import WikiartAPI
api = WikiartAPI()
image_path = api.get_painting('paul-cezanne')
```

The list of available artist name alias can be found by `api.artist_wikiart`. You can also use a name of an art movement.

```python
from wikiartcrawler import WikiartAPI
from wikiartcrawler import artist_group
api = WikiartAPI()

artist_group = artist_group.impressionism  # list of artist name
files = []
for artist in artist_group:
    files += api.get_painting(artist)
```

The `artist_group` method has `abstract-expressionism`, `baroque`, `ecole-de-paris`, `expressionism`, 
`impressionism`, `naive-art-primitivism`, `neo-impressionism`, `neoclassicism`, `post-impressionism`, 
`pre-raphaelite-brotherhood`, `realism`, `rococo`, `romanticism`, `surrealism`, and `symbolism`.

One can specify more fine-grained queries with `get_painting` as below.
```python
from wikiartcrawler import WikiartAPI
api = WikiartAPI()
# portrait only
api.get_painting('paul-cezanne', media=['oil', 'canvas'], style=['portrait'])
# landscape only
api.get_painting('paul-cezanne', media=['oil', 'canvas'], style=['landscape'])
```



### ArtFace Dataset

<p align="center">
  <img src="asset/overview.png" width="500">
</p>   


## Dataset Links
- Raw Images: The image files are divided by the art movement.
    * [`abstract-expressionism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/abstract_expressionism.zip)
    * [`baroque`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/baroque.zip)
    * [`ecole-de-paris`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/ecole_de_paris.zip)
    * [`expressionism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/expressionism.zip)
    * [`impressionism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/impressionism.zip)
    * [`naive-art-primitivism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/naive_art_primitivism.zip)
    * [`neo-impressionism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/neo_impressionism.zip)
    * [`neoclassicism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/neoclassicism.zip)
    * [`post-impressionism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/post_impressionism.zip)
    * [`pre-raphaelite-brotherhood`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/pre_raphaelite_brotherhood.zip)
    * [`realism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/realism.zip)
    * [`rococo`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/rococo.zip)
    * [`romanticism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/romanticism.zip)
    * [`surrealism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/surrealism.zip)
    * [`symbolism`](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/symbolism.zip)
- Face Image: 
