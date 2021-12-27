# WikiART Face/WikiART General Imageset & WikiART Crawler

<p align="center">
<img src="assets/wikiart_face.png" width="400"><br>
<em>Figure 1: Samples from WikiART Face dataset.</em>
</p>

This is an official repository of ***WikiART Crawler***, a python-library to download/process images from [WikiART](https://www.wikiart.org/) via WikiART API,
and two following image datasets created with the WikiART Crawler.
- [***WikiART Face***](#wikiart-face): Image dataset of face produced from the portraits attained via WikiART Crawler. 
- [***WikiART General***](#wikiart-general): Image dataset of paintings (landscape and portrait) attained via WikiART Crawler.

## WikiART Face

<p align="center">
<img src="assets/face_image_pipeline.png" width="500"><br>
<em>Figure 2: Pipeline to produce single WikiART Face image.</em>
</p>

WikiART Face is a collection of face from paintings. Inspired by the largest human-face image set [CelebA](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html),
we process all the portraits from WikiART with the pipeline described in Figure 2. 
As the final step, we blur the corner of each image so that model can pay more attention on the face rather than the background.
We release both version of the dataset w/wo the final blur step.   

## WikiART General

<p align="center">
  <img src="assets/wikiart_portrait.png" width="150">
  <img src="assets/wikiart_landscape.png" width="150">
  <img src="assets/wikiart_others.png" width="150"><br>
<br>
<em> Figure 3: Samples from WikiART General (`portrait`, `landscape`, `other` from left to right). </em>
</p>

WikiART General is 

If you are interested in the **WikiART Image Dataset** only, see [dataset section](#dataset-links).


## Basic Usage
First clone/install the library.
```shell
git clone https://github.com/asahi417/wikiart-crawler
cd wikiart-crawler
pip install .
```

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

## WikiArt Face
Inspired by [CelebA dataset](https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html), we release ***WikiArt Face*** that is an image dataset of face from portraits.

<p align="center">
  <img src="assets/wikiart_face.png" width="500">
</p>   

The entire pipeline to attain a face image from a portrait is described in the following diagram. 

<p align="center">
  <img src="assets/face_image_pipeline.png" width="500">
</p>

This image is available via the `wikiartcrawler` by specifying `image_type` argument.
```python
from wikiartcrawler import WikiartAPI
api = WikiartAPI()
# WikiArt Face  
files = api.get_painting('paul-cezanne', image_type='face')
# WikiArt Face (with background blur)
files = api.get_painting('paul-cezanne', image_type='face_blur')
```

To reproduce the WikiArt Face image set, you can use [these scripts](./examples/generate_face_data).

## Dataset Links
- ***WikiArt Image***: The image files are divided by the art movement.
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
- ***WikiArt Face***: See detail in the [WikiArt Face section](#wikiart-face).
  * [wikiart face](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/image_face.zip)
  * [wikiart face (with background blur)](https://github.com/asahi417/wikiart-crawler/releases/download/v0.0.0/image_face_blur.zip)
  
