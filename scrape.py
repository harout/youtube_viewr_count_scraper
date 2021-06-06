import requests
import re
from multiprocessing import Pool
from datetime import date

def get_channel_info(channel):
    channel_name = channel[0]
    channel_url = channel[1]
    page = requests.get(channel_url)
    print('Got results for ', channel_name)
    sub_count_search = re.search(r'subscriberCountText(.*?)"simpleText":"(.*?) subscribers"', page.text, re.M)
    num_subscribers = 'unknown subscriber count'
    if sub_count_search:
        num_subscribers = sub_count_search.group(2)
        if num_subscribers.endswith('K'):
            num_subscribers = str(round(float(num_subscribers[:-1]) * 1000))
        num_subscribers = num_subscribers.replace(',', '')


    num_views_search = re.search(r'viewCountText(.*?)"simpleText":"(.*?) views"', page.text, re.M)
    if not num_views_search:
        return [channel_name, channel_url, num_subscribers, 'unknown view count']

    num_views = num_views_search.group(2)
    num_views = num_views.replace(',', '')
    return [channel_name, channel_url, num_subscribers, num_views]


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
            ['The Yerevan Times','https://www.youtube.com/c/TheGamesWorld/about'],
            ['Yerevanyan Blog TV','https://www.youtube.com/c/YerevanyanBlog/about'],
            ['Sparta 1', 'https://www.youtube.com/channel/UCGxciBpj8fWpZIP805J1qVA/about'],
            ['Kristine Halajyan Քրիստինե Հալաջյան', 'https://www.youtube.com/channel/UCOKWS2GcPCEQ9VPx3Nkobcw/about'],
            ['Tert. am', 'https://www.youtube.com/user/tertamarmenia/about'],
            ['Suren Sargsyan', 'https://www.youtube.com/channel/UC-IEdDubp1Io--BquY-183g/about'],
            ['The Great Armenia', 'https://www.youtube.com/c/TheGreatArmenia/about'],
            ['PARATV', 'https://www.youtube.com/c/PARADIPLOMACYTV/about'],
            ['POLICE RA Vostikanutyun', 'https://www.youtube.com/c/Vostikanutyun/about'],
            ['Armenian National Network', 'https://www.youtube.com/c/ANNmedia/about'], 
            ['NVO1', 'https://www.youtube.com/channel/UCadQz-sg0lid5bxjqPc6Olg/about'],
            ['Armenian Second TV Channel / h2', 'https://www.youtube.com/c/armh2/about'],
            ['Ամերիկայի Ձայն VOA Armenian', 'https://www.youtube.com/c/VOAArmenian/about'],
            ['PastinfoTV', 'https://www.youtube.com/user/PastinfoTV/about'],
            ['ArmeniaTV News', 'https://www.youtube.com/channel/UCTeGnM60U9qoLH7ZZDhAsSg/about'],
            ['Vardan Hakobyan', 'https://www.youtube.com/c/VardanHakobyan/about'],
            ['Խոսենք Փաստերով TV', 'https://www.youtube.com/channel/UCZuKdeF9yfOjZ0J7AbBUOAw/about'],
            ['HetqTV', 'https://www.youtube.com/user/HetqTV/about'],
            ['Artsakh Public TV', 'https://www.youtube.com/channel/UC0bE8sdgd54oJBscXJfupCw/about'],
            ['Yerevan Today Live', 'https://www.youtube.com/c/YerevanTodayNews/about'],
            ['Hraparak TV', 'https://www.youtube.com/c/Hraparakdaily/about'],
            ['Աննա Աբրահամյան Իմ Հայաստան created DON DREAM','https://www.youtube.com/channel/UCuuqSVCWfMlwlwlfXSLIfKg/about'],
            ['Yerkir Media - News', 'https://www.youtube.com/user/YerkirmediaTV/about'],
            ['Yerkir Media Հաղորդումներ', 'https://www.youtube.com/channel/UCLqMTOyTNRVzavjJwZlFSvQ/about'],
            ['MenqHayenq Production', 'https://www.youtube.com/channel/UCUfcIB5azeiUD2egV7p7FEQ/about'],
            ['ԼՐԱՏՎԱԿԱՆ ՌԱԴԻՈ FM106.5', 'https://www.youtube.com/channel/UCaJCNkhSa84QcuOSoM2WfcA/about'],
            ['Repat Riarch', 'https://www.youtube.com/c/RepatRiarch_official/about'],
            ['New Channel tv', 'https://www.youtube.com/channel/UCDOG_qfxSvI-Dv1tkGpo8Dw/about'],
            ['HorizonArmenianTV', 'https://www.youtube.com/user/HorizonArmenianTV/about'],
            ['ARM GOOD INFO', 'https://www.youtube.com/channel/UCenBDno0RFwOg23Kr00kJVg/about'],
            ['Politik. am', 'https://www.youtube.com/c/Politikam2021/about'],
            ['armtimes.com', 'https://www.youtube.com/c/ArmtimesNewspaper/about'],
            ['Styop Grigoryan', 'https://www.youtube.com/user/123pepush/about'],
            ['AsekoseTV', 'https://www.youtube.com/channel/UCmsV3ead5PvSJwp6M6vik-A/about'],
            ['Aysor TV', 'https://www.youtube.com/user/AysorTV/about']
            ]

if __name__ == '__main__':
    with Pool(3) as p:
        results = p.map(get_channel_info, channels)
        for result in results:
            print(result[0] + "\t" + result[1] + "\t" + result[2] + "\t" + result[3])

    today = date.today()
    report_name = './data/channel_data_' + today.strftime("%B_%d_%Y") + '.tsv'
    with open(report_name, 'w') as f:
        f.write("name\turl\tsubscribers\tviews\n")
        for result in results:
            f.write(result[0] + "\t" + result[1] + "\t" + result[2] + "\t" + result[3] + "\n")
