from pytube import YouTube
from log import init_logger
from log import logger
import re

init_logger('jwli.log')


def download_youtube_video(video_url, title):
    title = re.sub(u"([^\u4e00-\u9fa5\u0030-"
                   u"\u0039\u0041-\u005a\u0061-\u007a])", " ", title)
    yt = YouTube(video_url)
    mp4 = yt.streams.first()
    logger.warning(f'{title} start')
    # print(f'{title}start')
    mp4.download('./youtube_video/', filename=f'{title}')
    logger.warning(f'{title} end')
    # print(f'{title}end')
