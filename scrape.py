import requests
import re

channels = [['Factor tv', 'http://www.youtube.com/c/Factortv/about'],
            ['a1Plus', 'https://www.youtube.com/c/a1plus/about'],
            ['armtimes', 'https://www.youtube.com/c/ArmtimesNewspaper/about']]


results = []
for channel in channels:
    channel_name = channel[0]
    channel_url = channel[1]
    page = requests.get(channel_url)
    sub_count_search = re.search(r'subscriberCountText(.*?)"simpleText":"(.*?) subscribers"', page.text, re.M)
    if not sub_count_search:
        results.append([channel_name, 'unknown subscriber count', 'unknown view count'])
        continue

    num_subscribers = sub_count_search.group(2)

    num_views_search = re.search(r'viewCountText(.*?)"simpleText":"(.*?) views"', page.text, re.M)
    if not num_views_search:
        results.append([channel_name, num_subscribers, 'unknown view count'])
        continue

    num_views = num_views_search.group(2)
    results.append([channel_name, num_subscribers, num_views])

for result in results:
    print(result[0] + '|' + result[1] + '|' + result[2])

