import requests
import json
import pandas as pd
import rename

'''得到所有会议的名称，指导url生成'''


def get_names():
    url = 'https://api.crossminds.io/content/category/parents/details'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'referer': 'https://crossminds.ai/explore/',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    names = []
    response = requests.get(url, headers=header)
    for i in range(len(response.json()['results'][0]['subcategory'])):
        names.append(response.json()['results'][0]['subcategory'][i]['name'])
    return names


'''把name中大写变小写，空格去掉'''


def name_transform(name):
    return name.lower().replace(' ', '')


'''初始化data'''


def set_init_data(limit, offset, category):
    data = {
        'limit': limit,
        'offset': offset,
        'search': {
            'category': category,
            'published_at': {'$ne': None}
        }
    }
    data = json.dumps(data)
    return data


def get_response(url, header, data):
    response = requests.post(url, headers=header, data=data)
    return response


def get_csv_data(results):
    csv_data = []
    for i in range(len(results)):
        s = rename.get_new_name2(results[i]['title'])
        temp = {
            'title': results[i]['title'],
            '_id': s,
            'abstract': results[i]['description'],
            'subjects': results[i]['category'][0],
            'videoUrl': results[i]['video_url'],
        }
        csv_data.append(temp)
    return csv_data


def run():
    baseUrl = 'https://api.crossminds.io/web/content/bycategory'
    header = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'referer': 'https://crossminds.ai/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    names = get_names()
    for name in names:
        name_trans = name_transform(name)
        data = set_init_data(24, 0, name)
        num = 0
        print(f'{name}爬取开始')
        while True:
            response = get_response(baseUrl, header, data)
            results = response.json()['results']
            csv_data = get_csv_data(results)
            df = pd.DataFrame(csv_data)

            if num == 0:
                df.to_csv(f'./outputfinal/{name_trans}.csv',
                          mode='a', index=False, encoding='utf-8')
            else:
                df.to_csv(f'./outputfinal/{name_trans}.csv', mode='a',
                          index=False, header=False, encoding='utf-8')
            csv_data.clear()
            num = num + len(results)
            data = json.dumps(response.json()['next_request'])
            if len(data) == 2:
                break
            # print(num)
        print(f'{name}爬取完成，共爬取{num}条数据')
    print('全部爬取完成')


if __name__ == '__main__':
    run()
