# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import codecs
import json
import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem
from crawler.dataManager import MongoManager, FileManager
from crawler.pdfToJson import run
import yaml
import logging

import re

with open('./conf/config.yaml', 'r', encoding="utf-8") as f:
    global_config = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
logging_config_file = './conf/logging_config.yaml'

# 设置日志
with open(logging_config_file, 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()
logger = logging.getLogger(__name__)


class ArxivcrawlerPipeline:
    def process_item(self, item, spider):
        return item


class ArxivcrawlerFilePipeline(FilesPipeline):

    # 必须要重写
    # 注意配置setting.py文件
    def get_media_requests(self, item, info):
        # print(item["paperUrl"])
        logger.info("Begin to download pdf from :" + item["paperPdfUrl"])
        yield scrapy.Request(item["paperPdfUrl"], meta={"item": item})

    # 重写设置路径
    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta["item"]
        file_name = item["_id"]
        return f"{file_name}.pdf"

    # 重写完成后的操作，比如文件路径，比如接入下游任务的提取文字任务
    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            logger.error("Can't download pdf from :" + item["paperPdfUrl"])
            return item

        item["paperPath"] = global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0]
        logger.info("Successful download pdf :" + item["paperPath"])
        try:
            item["paperContent"] = run.get_content(
                global_config["FILES_STORE"] + file_paths[0])
        except Exception as e:
            logger.error("Can't get pdf content :" + item["_id"])
            logger.error(e)
        finally:
            pass
        try:
            file_manager = FileManager(host=global_config["SSH_HOST"], port=global_config["SSH_PORT"],
                                       user_name=global_config["USER_NAME"], passwd=str(global_config["PASSWD"]))
            file_manager.upload_file(
                global_config["FILES_STORE"] + file_paths[0], global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0])
        except Exception as e:
            logger.error("Fail to upload pdf :" + item["_id"])
            logger.error(e)
        finally:
            return item
        return item


class ArxivJsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open("output.json", 'w')
        self.file.write("[\n")

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + ",\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        # self.file.seek(-1,1)
        self.file.write("]")
        self.file.close()


class ArxivPDFFetcherPipeline(FilesPipeline):

    def handle_redirect(self, file_url):  # 处理网页重定向
        '''response = requests.head(file_url)
        if response.status_code == 302:
            file_url = response.headers["Location"]'''
        file_url = file_url + ".pdf#pdfjs.action=download"
        return file_url

    def get_media_requests(self, item, info):
        logger.info("Begin to download pdf from :" + item["paperPdfUrl"])
        redirect_url = self.handle_redirect(item['paperUrl'])
        yield scrapy.Request(redirect_url, meta={'arxivNo': item['_id'], 'turnPage': False, "item": item}, priority=2)

    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta["item"]
        file_name = item["_id"]
        return f"{file_name}.pdf"

    def item_completed(self, results, item, info):
        paper_path = [x['path'] for ok, x in results if ok]
        if paper_path:
            item['paperPath'] = global_config["REMOTE_PAPER_PATH_PREFILX"] + paper_path[0]
            try:
                item["paperContent"] = run.get_content(
                    global_config["FILES_STORE"] + paper_path[0])
            except Exception as e:
                logger.error("Can't get pdf content :" + item["_id"])
                logger.error(e)
            finally:
                pass
            try:
                file_manager = FileManager(host=global_config["SSH_HOST"], port=global_config["SSH_PORT"],
                                           user_name=global_config["USER_NAME"], passwd=str(global_config["PASSWD"]))
                file_manager.upload_file(
                    global_config["FILES_STORE"] + paper_path[0], global_config["REMOTE_PAPER_PATH_PREFILX"] + paper_path[0])
            except Exception as e:
                logger.error("Fail to upload pdf :" + item["_id"])
                logger.error(e)
            finally:
                pass
        else:
            logger.error("Can't download pdf from :" + item["paperPdfUrl"])
        return item


class PapersWithCodeFilePipeline(FilesPipeline):

    # 必须要重写
    # 注意配置setting.py文件
    def get_media_requests(self, item, info):
        # print(item["paperUrl"])
        yield scrapy.Request(item["paperPdfUrl"], meta={"item": item})

    # 重写设置路径
    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta["item"]
        file_name = item["_id"]
        return f"{file_name}.pdf"

    # 重写完成后的操作，比如文件路径，比如接入下游任务的提取文字任务
    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            logger.error("Can't download pdf from :" + item["paperPdfUrl"])
            return item

        item["paperPath"] = global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0]
        logger.info("Successful download pdf :" + item["paperPath"])
        try:
            item["paperContent"] = run.get_content(
                global_config["FILES_STORE"] + file_paths[0])
        except Exception as e:
            logger.error("Can't get pdf content :" + item["_id"])
            logger.error(e)
        finally:
            pass
        try:
            file_manager = FileManager(host=global_config["SSH_HOST"], port=global_config["SSH_PORT"],
                                       user_name=global_config["USER_NAME"], passwd=str(global_config["PASSWD"]))
            file_manager.upload_file(
                global_config["FILES_STORE"] + file_paths[0], global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0])
        except Exception as e:
            logger.error("Fail to upload pdf :" + item["_id"])
            logger.error(e)
        finally:
            return item
        return item


class ACLPaperVideoFilePipeline(FilesPipeline):
    # 必须要重写
    # 注意配置setting.py文件
    def get_media_requests(self, item, info):
        if item['videoUrl'] != "":
            logger.info("Begin to download video from :" + item['videoUrl'])
            yield scrapy.Request(item['videoFileUrl'], meta={'item': item})
        else:
            logger.info("This item don't have video url:" + item["_id"])
            return item
    # 重写设置路径

    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta["item"]
        file_name = str(item["_id"])
        return f"{file_name}.mp4"

    # 重写完成后的操作，比如文件路径，比如接入下游任务的提取文字任务
    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            logger.error("Can't download video from :" + item["videoFileUrl"])
            return item
        item['videoPath'] = global_config["REMOTE_VIDEO_PATH_PREFILX"] + file_paths[0]
        logger.info("Successful download video :" + item["videoFileUrl"])

        try:
            file_manager = FileManager(host=global_config["SSH_HOST"], port=global_config["SSH_PORT"],
                                       user_name=global_config["USER_NAME"], passwd=str(global_config["PASSWD"]))
            file_manager.upload_file(
                global_config["FILES_STORE"] + file_paths[0], global_config["REMOTE_VIDEO_PATH_PREFILX"] + file_paths[0])
            if os.path.exists(global_config["FILES_STORE"] + file_paths[0]):
                os.remove(global_config["FILES_STORE"] + file_paths[0])
            else:
                print("The file does not exist")
        except Exception as e:
            logger.error("Fail to upload video :" + item["_id"])
            logger.error(e)
        finally:
            return item
        return item


class ACLPaperPdfFilePipeline(FilesPipeline):

    # 必须要重写
    # 注意配置setting.py文件
    def get_media_requests(self, item, info):
        if item['paperPdfUrl'] != "":
            logger.info("Begin to download pdf from :" + item['paperPdfUrl'])
            yield scrapy.Request(item['paperPdfUrl'], meta={'item': item})
        else:
            logger.info("This item don't have pdf url:" + item["_id"])
            yield item

    # 重写设置路径
    def file_path(self, request, response=None, info=None, *, item=None):
        item = request.meta["item"]
        file_name = str(item["_id"])
        return f"{file_name}.pdf"

    # 重写完成后的操作，比如文件路径，比如接入下游任务的提取文字任务
    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            logger.error("Can't download pdf from :" + item["paperPdfUrl"])
            return item

        item["paperPath"] = global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0]
        logger.info("Successful download pdf :" + item["paperPath"])
        try:
            item["paperContent"] = run.get_content(
                global_config["FILES_STORE"] + file_paths[0])
        except Exception as e:
            logger.error("Can't get pdf content :" + item["_id"])
            logger.error(e)
        finally:
            pass
        try:
            file_manager = FileManager(host=global_config["SSH_HOST"], port=global_config["SSH_PORT"],
                                       user_name=global_config["USER_NAME"], passwd=str(global_config["PASSWD"]))
            file_manager.upload_file(
                global_config["FILES_STORE"] + file_paths[0], global_config["REMOTE_PAPER_PATH_PREFILX"] + file_paths[0])
        except Exception as e:
            logger.error("Fail to upload pdf :" + item["_id"])
            logger.error(e)
        finally:
            return item
        return item


class MongoDbPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.mongodb = MongoManager(
            global_config["DATABASE_HOST"], global_config["DATABASE_PORT"])
        self.mongodb.select_db(global_config["DATABASE_NAME"])
        self.mongodb.select_col(global_config["DATABASE_COL"])

    def process_item(self, item, spider):
        self.mongodb.push_one(dict(item))
        return item


class PaperweeklyJsonPipeline(object):
    def __init__(self):
        base_dir = os.getcwd()
        filename = base_dir + '\\recommend_arxiv.json'
        self.file = codecs.open(filename=filename, mode='wb', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()
