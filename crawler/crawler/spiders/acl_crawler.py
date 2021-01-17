# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from crawler.items import CrawlerItem
import json
import re
import logging
import yaml

logging_config_file = './conf/logging_config.yaml'

# 设置日志
with open(logging_config_file, 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()
logger = logging.getLogger(__name__)


class AclwebSpider(scrapy.Spider):
    # 爬虫名
    name = 'aclweb'
    # 允许的域名
    allowed_domains = ['aclweb.org']
    # ACL中不同的会议
    # 修改venues 会议列表就可以了  没有写成 .txt 的形式 爬取的时候可以一个具体会议一个具体会议的爬取 例如 venues=['acl']
    venues = ['acl', 'anlp', 'cl', 'conlp', 'eacl', 'emnlp', 'aacl',
              'findings', 'naacl', 'semeval', '*sem', 'tacl', 'wmt', 'ws']
    base_url = "https://www.aclweb.org/anthology/venues/"
    venue = 0
    # 开始url
    # 'https://www.aclweb.org/anthology/venues/emnlp/'  #取到具体会议的url ，例如EMNLP
    start_urls = [base_url + venues[venue]]

    def parse(self, response):
        # //*[@id="main-container"]/div/div[2]/main/table[1]/tbody/tr/th/a/@href
        result = response.xpath(
            '//*[@id="main"]/div/div/div/ul/li/a/@href').extract()
        for i in result:
            # 取到一个会议的论文分类页面链接 例如EMNLP会议页面的paper分类页面链接
            url = urljoin('https://www.aclweb.org/', i)
            logger.info("正在处理该具体会议具体年份链接： " + url)
            yield scrapy.Request(url, callback=self.all_papers_parse, dont_filter=True)
            logger.info("已完成对该具体会议具体年份链接 " + url + " 的处理")
        if self.venue < 14:
            self.venue += 1
            logger.info("开始处理会议：" + self.venues[self.venue])
            emnlpurl = self.base_url + self.venues[self.venue]
            logger.info("处理会议：" + emnlpurl)
            yield scrapy.Request(emnlpurl, callback=self.parse, dont_filter=True)

    def all_papers_parse(self, response):

        result0 = response.xpath(
            '//*[@id="main"]/div[2]/p/span[2]/strong/a/@href').extract()
        for j in result0:
            url1 = urljoin('https://www.aclweb.org/', j)
            logger.info("处理具体年份会议某一Content：" + url1)
            yield scrapy.Request(url=url1, callback=self.parse_paper)

    def parse_paper(self, response):
        item = CrawlerItem()
        papernames = response.xpath('//*[@id="title"]/a')
        name = ""
        for i, papername in enumerate(papernames):
            name += str(papername.xpath('//text()').extract()[0])
        # response.xpath('//*[@id="title"]/a/text()').extract()
        item['title'] = name[:-16]
        item['abstract'] = response.xpath(
            '//*[@id="main"]/div/div[1]/div/div/text()').extract()
        if len(item['abstract']) > 0:
            item['abstract'] = str(item['abstract'][0])
        else:
            item['abstract'] = ""

        item['doi'] = response.xpath('//*[@id="main"]/div/div[1]/dl/dd[13]/a/text()').extract()
        if len(item['doi']) > 0:
            item['doi'] = str(item['doi'][0])
        else:
            item['doi'] = ""

        item['_id'] = "".join(filter(str.isalnum, item['title'])).lower()

        item['subjects'] = "nlp"

        tmp_month = response.xpath(
            '//*[@id="main"]/div/div[1]/dl/dd[3]/text()').extract()
        if len(tmp_month) > 0:
            tmp_month = str(tmp_month[0])
        else:
            tmp_month = ""
        item['year'] = response.xpath(
            '//*[@id="main"]/div/div[1]/dl/dd[4]/text()').extract()
        if len(item['year']) > 0:
            item['year'] = str(item['year'][0])
        else:
            item['year'] = ""
        item["year"] = item["year"]

        item['publisher'] = response.xpath(
            '//*[@id="main"]/div/div[1]/dl/dd[8]/text()').extract()
        if len(item['publisher']) > 0:
            item['publisher'] = str(item['publisher'][0])
        else:
            item['publisher'] = ""
        item['paperUrl'] = response.xpath(
            '//*[@id="main"]/div/div[1]/dl/dd[12]/a/@href').extract()
        if len(item['paperUrl']) > 0:
            item['paperUrl'] = str(item['paperUrl'][0])
        else:
            item['paperUrl'] = ""

        if (len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()) > 0
                and str(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()[0]) == 'PDF:'):
            item['paperPdfUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[16]/a/@href').extract()
        else:
            item['paperPdfUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[15]/a/@href').extract()

        item_authors = response.xpath('//*[@id="main"]/p//text()').extract()
        allname = []
        for names in item_authors:
            if names == ',\n':
                continue
            name_split = str(names).split(" ")

            firstName = " ".join(name_split[:-1])
            lastName = "".join(name_split[-1:])
            allname.append({"firstName": firstName,
                            "lastName": lastName})

        item['authors'] = allname
        if(len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[17]/text()').extract()) > 0
                and str(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[17]/text()').extract()[0]) == 'Dataset:'):
            item['datasetUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[17]/a/@href').extract()
        elif(len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()) > 0
                and str(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()[0]) == 'Dataset:'):
            item['datasetUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[16]/a/@href').extract()
        else:
            item['datasetUrl'] = ""

        if (len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[18]/text()').extract()) > 0 and str(
                response.xpath('//*[@id="main"]/div/div[1]/dl/dt[18]/text()').extract()[0]) == 'Video:'):
            item['videoUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[18]/a/@href').extract()
        elif (len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[17]/text()').extract()) > 0 and str(
                response.xpath('//*[@id="main"]/div/div[1]/dl/dt[17]/text()').extract()[0]) == 'Video:'):
            item['videoUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[17]/a/@href').extract()
        elif (len(response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()) > 0 and str(
                response.xpath('//*[@id="main"]/div/div[1]/dl/dt[16]/text()').extract()[0]) == "Video:"):
            item['videoUrl'] = response.xpath(
                '//*[@id="main"]/div/div[1]/dl/dd[16]/a/@href').extract()
        else:
            item['videoUrl'] = ""

        if item['paperPdfUrl'] != "" and len(item['paperPdfUrl']) > 0:
            item['paperPdfUrl'] = str(item['paperPdfUrl'][0])
            item['paperPath'] = ""
        else:
            item['paperPdfUrl'] = ""
            item['paperPath'] = ""

        if item['videoUrl'] != "" and len(item['videoUrl']) > 0:

            # slideslive.com 视频网站 2020 视频全在这个网站上
            if str(item['videoUrl']).count("slideslive.com") > 0:
                item['videoUrl'] = str(item['videoUrl'][0])
                videoNum = str(item['videoUrl']).split("/")[-1]  #
                getServiceNumBaseUrl = "https://ben.slideslive.com/player/"
                getServiceNumBaseUrl += videoNum + "?demo=false"
                yield scrapy.Request(url=getServiceNumBaseUrl, meta={'item': item}, callback=self.parse_slideslive_video_url,
                                     dont_filter=True)
            # vimeo.com 视频网站 2020之前视频全在这个网站上
            elif str(item['videoUrl']).count("vimeo.com") > 0:
                videoNum = str(item['videoUrl']).split(
                    "/")[-1]  # https://vimeo.com/305204297
                getVideoFileUrl = "https://player.vimeo.com/video/" + videoNum + \
                    "/config?autopause=1&byline=0&collections=1&context=Vimeo%5CCo" + \
                    "ntroller%5CClipController.main&default_to_hd=1&outro=nothing&portrait=" + \
                    "0&share=1&title=0&watch_trailer=0&s=b80e87994a82ae61756aacaa4290cd7392ddc270_1609659460"

                yield scrapy.Request(url=getVideoFileUrl, meta={'item': item}, callback=self.parse_vimeo_videofile_url,
                                     dont_filter=True)
            else:
                yield item
        else:
            item['videoUrl'] = ""
            item['videoPath'] = ""
            item['videoFileUrl'] = ""
            yield item

    def parse_vimeo_videofile_url(self, response):
        pattern = re.compile(
            r'"url":"https://vod-progressive.akamaized.net/exp=([0-9]+)(~)([a-zA-Z]+)(=%)([a-zA-Z0-9=%-.~/]+)*(.mp4)',
            re.I)  # 查找.mp4 url地址的正则表达式

        result_list = pattern.findall(str(response.text))
        video360_url = "https://vod-progressive.akamaized.net/exp="
        if len(result_list) > 0:
            base360 = result_list[0]
            for i in base360:
                video360_url += i
        else:
            video360_url = ""
        item = response.meta['item']
        # import pdb;
        # pdb.set_trace()
        item["videoFileUrl"] = video360_url
        yield item

    def parse_slideslive_video_url(self, response):
        video_service_id = json.loads(response.text)["video_service_id"]
        video2020BaseUrl = "https://player.vimeo.com/video/" + video_service_id
        + "?loop=false&autoplay=false&byline=false&portrait=false&title=false&r"
        + "esponsive=true&speed=true&dnt=true&controls=true"
        yield scrapy.Request(url=video2020BaseUrl, meta={'item': response.meta['item']},
                             callback=self.parse_slideslive_video_file, dont_filter=True)

    def parse_slideslive_video_file(self, response):
        pattern = re.compile(
            r'"url":"https://vod-progressive.akamaized.net/exp=([0-9]+)(~)([a-zA-Z]+)(=%)([a-zA-Z0-9=%-.~/]+)*(.mp4)',
            re.I)  # 查找.mp4 url地址的正则表达式

        result_list = pattern.findall(
            str(response.xpath('/html/body/script[1]/text()').extract()))

        video360_url = "https://vod-progressive.akamaized.net/exp="
        if len(result_list) > 0:
            base360 = result_list[0]
            for i in base360:
                video360_url += i
        else:
            video360_url = ""

        item = response.meta['item']
        item["videoFileUrl"] = video360_url
        yield item

        # import pdb;
        # pdb.set_trace()
