import scrapy
from crawler.items import CrawlerItem
import logging
import yaml

import re
import datetime

logging_config_file = './conf/logging_config.yaml'

# 设置日志
with open(logging_config_file, 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()
logger = logging.getLogger(__name__)


class ArxivAutoSpider(scrapy.Spider):
    name = 'arxivAutoSpider'
    allowed_domains = ['arxiv.org']
    arxiv_domain = "https://arxiv.org"
    # start_urls = ['https://arxiv.org/']
    # 爬取之前输入想要catch up的年份月份
    # 获取当前的时间得到打印的终止点（根据这个也能知道需要catch up的总月份），log打印每年每月的爬取进度
    # catch_up = input("Catch up from year-month(e.g.2020-01):")
    catch_up = "2020-01"
    cut_num = 500
    start_year = catch_up[0:4]
    start_month = catch_up[5:7]
    skip_point = '0'
    show_step = '200'
    end_year, end_month, day_now = tuple(re.findall(
        r'[1-9]\d*', datetime.datetime.now().strftime('%Y-%m-%d')))
    end_month = end_month.zfill(2)
    start_url = "https://arxiv.org/list/cs/" + \
        start_year[2:4] + start_month + "?" + \
        "skip=" + skip_point + "&show=" + show_step
    start_urls = [start_url]  # 开始地址根据目前爬取进度决定
    '''timeStamp = datetime.datetime.now()
    whichIP = 0 # 1使用代理IP,0使用本地IP'''

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"turnPage": True})

    def parse(self, response):
        # 这里从每月的页面上爬取每个论文展示页面的URL，如果是最后一个月则跳到下一年的一月重新开始
        # 爬取本页的paper链接
        paper_links = response.xpath(
            "//*[@id='dlpage']/dl/dt/span/a[1]/@href").extract()
        print(paper_links, len(paper_links))
        for link in paper_links:
            full_link = self.arxiv_domain + link
            # 页内爬取的请求优先级高于翻页请求
            yield scrapy.Request(full_link, callback=self.parse_paper,
                                 meta={'turnPage': False, "paperYear": self.start_year}, priority=1)

        # 本月内翻页
        page_mark = response.xpath(
            "//*[@id='dlpage']/small[1]/b/text()").extract()
        all_marks = response.xpath(
            "//*[@id='dlpage']/small[1]/a/text()").extract()
        logger.info("-------------------------" + self.start_year + "." + self.start_month
                    + "crawlingPapers: " + page_mark[0] + "-------------------------")
        page_mark = int(re.findall(r'-?\d+', page_mark[0])[0])
        last_mark = int(re.findall(r'-?\d+', all_marks[-1])[0])
        print(page_mark, last_mark)
        if page_mark < last_mark:
            self.skip_point = str(int(self.skip_point) + int(self.show_step))
            next_page = "https://arxiv.org/list/cs/" + \
                self.start_year[2:4] + self.start_month + "?" + \
                "skip=" + self.skip_point + "&show=" + self.show_step
            yield scrapy.Request(next_page, callback=self.parse, meta={"turnPage": True})
        else:  # 翻到最后一页了，准备开始爬下一个月的
            logger.info("-------------------------" + self.start_year + "." + self.start_month
                        + "crawlingPapers:" + "ALL DONE" + "-------------------------" + "\n")
            self.skip_point = '0'
            if self.start_month == "12":
                self.start_year = str(int(self.start_year) + 1)
                self.start_month = "01"
            else:
                self.start_month = str(int(self.start_month) + 1).zfill(2)
            if int(self.start_year + self.start_month) < int(self.end_year + self.end_month):
                next_month = "https://arxiv.org/list/cs/" + \
                    self.start_year[2:4] + self.start_month + "?" + \
                    "skip=" + self.skip_point + "&show=" + self.show_step
                # time.sleep(600) # 睡眠10mins
                yield scrapy.Request(next_month, callback=self.parse, meta={"turnPage": True})
            else:  # 更新完成
                # print("-------------------------", "crawlingEnd:", "Up-to-date already.", "-------------------------", "\n")
                logger.info("-------------------------" + "crawlingEnd: "
                            + "Up-to-date already." + "-------------------------" + "\n")

    def parse_paper(self, response):  # 爬取单个paper信息
        print("parse_status:", response.status)
        item = CrawlerItem()
        item['arxiv_id'] = response.xpath(
            '//span[@class="arxivid"]/a/text()').extract_first()  # arxiv编号
        item['title'] = response.xpath(
            "//*[@id='abs']/h1/text()").extract_first()  # 论文标题
        item['_id'] = item['title'].replace(" ", "").casefold()
        item['publisher'] = "arxiv"
        authors = response.xpath(
            '//div[@class="authors"]/a/text()').extract()  # 作者
        item['authors'] = []
        for author in authors:
            first_name, space, last_name = author.rpartition(" ")
            item['authors'].append(
                {"first_name": first_name, "last_name": last_name})
        item['year'] = response.meta['paperYear']
        item['abstract'] = response.xpath(
            '//*[@id="abs"]/blockquote/text()').extract()[1].replace('\n', '')
        item['subjects'] = response.xpath(
            '//span[@class="primary-subject"]/text()').extract_first()
        paperUrl = response.xpath(
            '//div[@class="full-text"]//a[@class="abs-button download-pdf"]/@href').extract_first()
        if paperUrl:
            item['paperUrl'] = self.arxiv_domain + paperUrl
            item['paperPdfUrl'] = item['paperUrl'] + \
                ".pdf#pdfjs.action=download"
        else:
            pass
        # codelink = response.xpath('//*[@id="pwc-output"]//a/@href').extract_first()
        '''if codelink.find('paperwithcode'):
            item['codeUrl'] = codelink'''
        # item['crawlDate'] = self.start_year + '-' + self.start_month
        # item['enProxy'] = response.meta['en_proxy']
        yield item


class ArxivSpider(scrapy.Spider):
    name = 'arxivSpider'
    allowed_domains = ['arxiv.org']
    arxiv_domain = "https://arxiv.org"
    start_urls = []
    with open("./start_urls.txt", "r") as f:
        url = f.readline().replace("\n", "")
        while url:
            start_urls.append(url)
            url = f.readline().replace("\n", "")

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"turnPage": True})

    def parse(self, response):  # 这里从每月的页面上爬取每个论文展示页面的URL，如果是最后一个月则跳到下一年的一月重新开始
        # 爬取本页的paper链接
        paper_links = response.xpath(
            "//*[@id='dlpage']/dl/dt/span/a[1]/@href").extract()
        year = re.findall(r'-?\d+', response.url)[0][0:2]
        print(paper_links, len(paper_links))
        for link in paper_links:
            full_link = self.arxiv_domain + link
            # 页内爬取的请求优先级高于翻页请求
            yield scrapy.Request(full_link, callback=self.parse_paper,
                                 meta={'turnPage': False, "paperYear": "20" + year}, priority=1)

    def parse_paper(self, response):  # 爬取单个paper信息
        print("parse_status:", response.status)
        item = CrawlerItem()
        item['arxiv_id'] = response.xpath(
            '//span[@class="arxivid"]/a/text()').extract_first()  # arxiv编号
        item['title'] = response.xpath(
            "//*[@id='abs']/h1/text()").extract_first()  # 论文标题
        item['_id'] = "".join(filter(str.isalnum, item['title'])).lower()
        item['publisher'] = "arxiv"
        authors = response.xpath(
            '//div[@class="authors"]/a/text()').extract()  # 作者
        item['authors'] = []
        for author in authors:
            first_name, space, last_name = author.rpartition(" ")
            item['authors'].append(
                {"first_name": first_name, "last_name": last_name})
        item['year'] = response.meta['paperYear']
        item['abstract'] = response.xpath(
            '//*[@id="abs"]/blockquote/text()').extract()[1].replace('\n', '')
        item['subjects'] = response.xpath(
            '//span[@class="primary-subject"]/text()').extract_first()
        paperUrl = response.xpath(
            '//div[@class="full-text"]//a[@class="abs-button download-pdf"]/@href').extract_first()
        if paperUrl:
            item['paperUrl'] = self.arxiv_domain + paperUrl
            item['paperPdfUrl'] = item['paperUrl'] + \
                ".pdf#pdfjs.action=download"
        else:
            pass
        # codelink = response.xpath('//*[@id="pwc-output"]//a/@href').extract_first()
        '''if codelink.find('paperwithcode'):
            item['codeUrl'] = codelink'''
        # item['crawlDate'] = self.start_year + '-' + self.start_month
        # item['enProxy'] = response.meta['en_proxy']
        yield item
