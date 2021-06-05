import requests
import re

channels = [['Factor tv', 'http://www.youtube.com/c/Factortv/about'],
            ['a1Plus', 'https://www.youtube.com/c/a1plus/about'],
            ['armtimes', 'https://www.youtube.com/c/ArmtimesNewspaper/about'],
            ['azatutyun radio', 'https://www.youtube.com/c/azatutyunradio/about'],
            ['perfect tv', 'https://www.youtube.com/channel/UC8kOchMgfcXZTDtgQ67LM9Q/about'],
            ['ArmNkr News', 'https://www.youtube.com/channel/UCOcuOF0M-rZ5QzKTvr1J8IQ/about'],
            ['Vardan Ghukasyan Վարդան Ղուկասյան', 'https://www.youtube.com/channel/UChXhis-jyFXzMw4o9hML3vA/about'],
            ['24TV', 'https://www.youtube.com/c/24TVArmenia/about'],
            ['365daily am', 'https://www.youtube.com/channel/UCGOYnPqyWiPwPdlvUlfuNcQ/about'],
            ['NEWS AM','https://www.youtube.com/c/NewsamChannel/about'],
            ['STP ARM NEWS','https://www.youtube.com/c/STPmusicRAP/about'],
            ['ArmLur official','https://www.youtube.com/channel/UChjW08B983y0T2NvktcIjfg/about'],
            ['1in.am', 'https://www.youtube.com/c/1inam/about'],
            ['HAYELI AM','https://www.youtube.com/c/Hayeliam_Hayeli_Akumb/about'],
            ['8rd. am', 'https://www.youtube.com/channel/UCzQMSe3jpEVDTJa9jy9eEZA/about'],
            ['YELAKET / Yelaket News Agency /', 'https://www.youtube.com/c/YelaketNewsAgency/about'],
            ['Armenian Public TV', 'https://www.youtube.com/c/ArmenianPublicTV/about'],
            ['5 TV Channel', 'https://www.youtube.com/c/AraratTv/about'],
            ['SHD ARM TV', 'https://www.youtube.com/c/SHDARMTV/about'],
            ['amenor am', 'https://www.youtube.com/channel/UCfqS6YahbpwtWQRCJNOyVEw/about'],
            ['AREG TV','https://www.youtube.com/c/aregtv/about'],
            ['8rd news', 'https://www.youtube.com/channel/UC0uK3jBxj6ioFn5-XsleQKA/about'],
            ['Asekose am','https://www.youtube.com/user/ASEKOSEful/about'],
            ['ArmNews', 'https://www.youtube.com/user/ArmnewsTV/about'],
            ['ARTN TV', 'https://www.youtube.com/channel/UCGto6lM2ggZi4Ut4GHo31XA/about'],
            ['ArmLur TV', 'https://www.youtube.com/c/ArmLurTV/about'],
            ['ԼՈՒՐԵՐ Նորություններ Հայաստանից', 'https://www.youtube.com/user/LURERcom/about'],
            ['ArmeniaNow', 'https://www.youtube.com/c/ArmeniaNow/about'],
            ['SecretTube', 'https://www.youtube.com/channel/UCTRRvh0-lR9rPaC0nzNYFMA/about'],
            ['Բաց TV','https://www.youtube.com/channel/UCf2o81mWr-bZsLbq2-kOYTQ/about'],
            ['CIVILNET', 'https://www.youtube.com/c/CivilNetTV/about'],
            ['iravabannet', 'https://www.youtube.com/user/iravabannet/about'],
            ['AD TV', 'https://www.youtube.com/channel/UC8k_9xHrn82EV_oSFXBE6Cw/about'],
            ['Live News', 'https://www.youtube.com/channel/UCCllZTHrcly_pkPvb_V1ovA/about'],
            ['Novosti-Armenia', 'https://www.youtube.com/c/NovostiArmenia/about'],
            ['Kentron Channel', 'https://www.youtube.com/c/KentronChannel/about'],
            ['Tv9 am', 'https://www.youtube.com/c/Tv9am/about'],
            ['ԱԶԳԱՅԻՆ - ԺՈՂՈՎՐԴԱՎԱՐԱԿԱՆ ԲԵՎԵՌ','https://www.youtube.com/user/preparliament/about'],
            ['SHANT NEWS', 'https://www.youtube.com/c/SHANTNEWS/about'],
            ['The Yerevan Times','https://www.youtube.com/c/TheGamesWorld/about']
            
            ]



results = []
for channel in channels:
    channel_name = channel[0]
    channel_url = channel[1]
    page = requests.get(channel_url)
    sub_count_search = re.search(r'subscriberCountText(.*?)"simpleText":"(.*?) subscribers"', page.text, re.M)
    num_subscribers = 'unknown subscriber count'
    if sub_count_search:
        num_subscribers = sub_count_search.group(2)
        if num_subscribers.endswith('K'):
            num_subscribers = str(round(float(num_subscribers[:-1]) * 1000))
        num_subscribers = num_subscribers.replace(',', '')


    num_views_search = re.search(r'viewCountText(.*?)"simpleText":"(.*?) views"', page.text, re.M)
    if not num_views_search:
        results.append([channel_name, num_subscribers, 'unknown view count'])
        continue

    num_views = num_views_search.group(2)
    num_views = num_views.replace(',', '')
    results.append([channel_name, num_subscribers, num_views])

for result in results:
    print(result[0] + "\t" + result[1] + "\t" + result[2])

