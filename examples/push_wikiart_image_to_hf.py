import json
import os.path
from glob import glob
from datasets import load_dataset, DatasetDict
from wikiartcrawler import artist_group


artist2group = {}
for v in artist_group.VALID_ARTIST_GROUPS:
    artists = artist_group.load_artists(v)
    artist2group.update({a: v for a in artists})


def parse_meta_data(meta_data: str, image_dir: str):
    meta_all = []
    for meta in glob(f"{meta_data}/*.json"):
        with open(meta) as f:
            meta_data = json.load(f)
            for data in meta_data:
                detail = data.pop("detail")
                detail.update(data)
                if detail['artistUrl'] not in artist2group:
                    detail["group"] = "unknown"
                else:
                    detail["group"] = artist2group[detail['artistUrl']]
                tmp = f'{image_dir}/image_face.{detail["artistUrl"]}.{detail["url"]}'
                tmp = glob(f"{tmp}.*")
                if len(tmp) == 1:
                    detail["file_name"] = os.path.basename(tmp[0])
                    meta_all.append(detail)
    return meta_all

meta_all = parse_meta_data(
    "/home/c.c2042013/wikiartcrawler_cache/meta",
    "/home/c.c2042013/wikiartcrawler_cache/dataset/test"
)
len(meta_all)
with open("test/metadata.jsonl", "w") as f:
    f.write("\n".join([json.dumps(i) for i in meta_all]))

filenames = [i["file_name"] for i in meta_all]
images = glob("/home/c.c2042013/wikiartcrawler_cache/dataset/test/*")
missing = []
for i in images:
    if os.path.basename(i) not in filenames:
        missing.append(i)
for i in missing:
    os.remove(i)
dataset = load_dataset("imagefolder", data_dir=".")
dataset = DatasetDict({"test": dataset})
dataset.push_to_hub("asahi417/wikiart_face")



def parse_meta_data(meta_data: str, image_dir: str):
    meta_all = []
    for meta in glob(f"{meta_data}/*.json"):
        with open(meta) as f:
            meta_data = json.load(f)
            for data in meta_data:
                detail = data.pop("detail")
                detail.update(data)
                if detail['artistUrl'] not in artist2group:
                    detail["group"] = "unknown"
                else:
                    detail["group"] = artist2group[detail['artistUrl']]

                tmp = f'{image_dir}/{detail["group"]}.{detail["artistUrl"]}.{detail["url"]}'
                tmp = glob(f"{tmp}.*")
                if len(tmp) == 1:
                    detail["file_name"] = os.path.basename(tmp[0])
                    meta_all.append(detail)
    return meta_all

meta_all = parse_meta_data(
    "/home/c.c2042013/wikiartcrawler_cache/meta",
    "/home/c.c2042013/wikiartcrawler_cache/files"
)
with open("metadata.jsonl", "w") as f:
    f.write("\n".join([json.dumps(i) for i in meta_all]))

dataset = load_dataset("imagefolder", data_dir=".")
