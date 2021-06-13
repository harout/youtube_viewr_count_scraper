import requests
import re
from multiprocessing import Pool
from datetime import date
import json


def get_video_info(video_url):
    page = requests.get(video_url)
    yt_initial_data_search = re.search(r'<script nonce=".*?">.*?var ytInitialData = (.*?);</script>', page.text, re.M)
    if not yt_initial_data_search:
        return None

    response_json = yt_initial_data_search.group(1)
    try:
        response = json.loads(response_json)
        video_data_objs = response['contents']['twoColumnWatchNextResults']['results']['results']['contents']
        for data in video_data_objs:
            if 'videoPrimaryInfoRenderer' in data:
                data = data['videoPrimaryInfoRenderer']
                view_count = data['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
                view_count = view_count.split(' ')[0]
                title = data['title']['runs'][0]['text']
                like_fraction = data['sentimentBar']['sentimentBarRenderer']['tooltip']
                like_split = like_fraction.split(' / ')
                like, dislike = like_split[0], like_split[1]
                create_date = data['dateText']['simpleText']
                return {'title': title,
                        'url': video_url,
                        'created': create_date,
                        'views': view_count,
                        'likes': like,
                        'dislikes': dislike}
    except:
        return None
  

video_urls = ['https://www.youtube.com/watch?v=PIoHE4L09Co',
              'https://www.youtube.com/watch?v=Llg9Gl_-zd4',
              'https://www.youtube.com/watch?v=MhwmIgbQY64',
              'https://www.youtube.com/watch?v=6_qIHwubuw0'  
             ]

if __name__ == '__main__':
    with Pool(3) as p:
        results = p.map(get_video_info, video_urls)

    today = date.today()
    report_name = './data/video_data_' + today.strftime("%B_%d_%Y") + '.tsv'
    with open(report_name, 'w') as f:
        f.write("url\ttitle\tcreated\tviews\tlikes\tdislikes\n")
        for result in results:
            title = result['title'].replace("\t", ' ')
            f.write(result['url'] + "\t" + title + "\t" + result['created'] + "\t" + result['views'] + "\t" + result['likes'] + "\t" + result['dislikes'] + "\n")
