import requests
import re
import os
from urllib import parse
from log import init_logger
from log import logger

init_logger('jwli.log')


def getProxies():
    response = requests.get('http://10.4.20.69:5010/get')
    proxy = response.json()['proxy']
    proxies = {
        'http': proxy,
        'https': None
    }
    return proxies


def get_m3u8_test(url):
    r = requests.get(url, proxies=getProxies())
    # print(r.text)
    return r.text


def get_ts_url_list(m3u8_text, url):
    pattern_ts = re.compile('.*?\\.ts')
    ts_list = pattern_ts.findall(m3u8_text)
    ts_url_list = []
    for ts in ts_list:
        ts_url = parse.urljoin(url, ts)
        ts_url_list.append(ts_url)
    # print(ts_url_list)
    return ts_url_list


def write_ts(ts_url_list, ts_path):
    logger.warning('----开始下载----')
    # print('----开始下载----')
    if not os.path.exists(ts_path):
        os.makedirs(ts_path)
    for i, ts_url in enumerate(ts_url_list):
        con = requests.get(ts_url, proxies=getProxies()).content
        with open(f'{ts_path}{i}.ts', 'wb') as fw:
            fw.write(con)


def download_m3u8_video(ts_path, save_path, title):
    ts_list = os.listdir(ts_path)
    with open(f'{save_path}', 'ab') as fw:
        for i in range(len(ts_list)):
            with open(f'./m3u8/{title}/{i}.ts', 'rb') as fr:
                fw.write(fr.read())


def download(url, title):
    title = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-"
                   u"\u005a\u0061-\u007a])", " ", title)
    base_ts_path = './m3u8/'
    ts_path = base_ts_path + title + '/'
    # print(ts_path)
    # exit()
    save_path = f'./m3u8_video/{title}.mp4'

    m3u8_test = get_m3u8_test(url)
    ts_url_list = get_ts_url_list(m3u8_test, url)
    write_ts(ts_url_list, ts_path)

    download_m3u8_video(ts_path, save_path, title)
    logger.warning(f'{title}下载完成!')
    # print(f'{title}下载完成!')
