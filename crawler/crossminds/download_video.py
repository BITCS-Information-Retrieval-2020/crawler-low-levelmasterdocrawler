import download_m3u8_video as m3u8
import download_youtube_video as youtube
import os
import threadpool
import pandas as pd
import time
from log import init_logger
from log import logger

init_logger('jwli.log')


def run_one_thread(row):
    logger.info(row['video_url'])
    # print(row['video_url'])
    i = 0
    while True:
        try:
            if row['source'] == 'CrossMinds':
                logger.info('这是一个m3u8视频')
                # print('这是一个m3u8视频')
                m3u8.download(row['video_url'], row['title'])
            elif row['source'] == 'YouTube download':
                logger.info('这是一个youtube视频')
                # print('这是一个youtube视频')
                youtube.download_youtube_video(row['video_url'], row['title'])
            else:
                logger.info('这是个什么东西？')
            break
        except Exception as e:
            i = i + 1
            logger.warning(e)
            logger.warning(f"{row['title']},{row['video_url']}重试")
            if i > 10:
                break
            time.sleep(10)


def run_pthread(rows):
    pool = threadpool.ThreadPool(len(rows))
    requests = threadpool.makeRequests(run_one_thread, rows)
    for req in requests:
        pool.putRequest(req)
        time.sleep(10)
    pool.wait()


def run():
    csv_list = os.listdir('./output/')
    i = 0
    for filename in csv_list:
        logger.info(f'filename={filename.format()}')
        # print(f'filename={filename.format()}')
        i = i + 1
        df = pd.read_csv(f'./output/{filename}', encoding='utf-8')
        # print(df)
        # print(type(df))
        rows = []
        for index, row in df.iterrows():
            rows.append(row)
        run_pthread(rows)
        logger.warning(f'------------第{i}轮已经爬取完成------------')
        # print((f'第{i}伦已经爬取完成'))


if __name__ == '__main__':
    run()
