import pandas as pd
from wikiartcrawler import WikiartAPI, get_artist, VALID_ARTIST_GROUPS
# all_artists = artist_group.available_artist()


api = WikiartAPI(skip_download=True)


def get_stats(arguments=None):
    stats = {}
    all_files = []
    for g in VALID_ARTIST_GROUPS:
        artists = get_artist(g)
        files = []
        for a in artists:
            if arguments is None:
                tmp = api.get_painting(a)
            else:
                tmp = api.get_painting(a, **arguments)
            if tmp is not None:
                files += tmp
        print('\t {}: {} images'.format(g, len(files)))
        stats[g] = len(files)
        all_files += files
    stats['All'] = len(list(set(all_files)))
    print('* total: {} images'.format(len(list(set(all_files)))))
    return stats


df = {}
print('\n\nWikiART Face')
df['WikiART Face'] = get_stats(arguments={'image_type': 'face_blur'})

print('\n\nWikiART General (all)')
df['WikiART General'] = get_stats(arguments={'media': ['oil', 'canvas']})

print('\n\nWikiART General (portrait)')
df['WikiART General/Portrait'] = get_stats(arguments={'media': ['oil', 'canvas'], 'genre': ['portrait']})

print('\n\nWikiART General (landscape)')
df['WikiART General/Landscape'] = get_stats(arguments={'media': ['oil', 'canvas'], 'genre': ['landscape']})


print(VALID_ARTIST_GROUPS)
df = pd.DataFrame(df)
df['WikiART General/Other'] = df['WikiART General'] - df['WikiART General/Landscape'] - df['WikiART General/Portrait']
df_ = df.pop('WikiART Face')
print(df_.to_markdown())
print(df.to_markdown())
df_.to_csv('./assets/stats.face.csv')
df.to_csv('./assets/stats.csv')
