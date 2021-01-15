# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # _id:唯一标识符，title只保留英文字母并转小写
    _id = scrapy.Field()
    # arxiv上编码，没有则为空
    arxiv_id = scrapy.Field()
    # 出版的论文都有的编码，arxiv上没有，没有为空
    doi = scrapy.Field()
    # 论文标题
    title = scrapy.Field()
    # 作者，样例[{first name: "df", second_name: "v"}, {first name: "a", second_name: "b"}]
    authors = scrapy.Field()
    # 年份， YYYY格式（如2020）
    year = scrapy.Field()
    # 出版商，acl，arxiv等等
    publisher = scrapy.Field()
    # 摘要
    abstract = scrapy.Field()
    # 分类，nlp，cv这种
    subjects = scrapy.Field()
    # 论文PDF的url
    paperUrl = scrapy.Field()
    # 论文代码url，没有为空，格式事list，即为[]
    codeUrl = scrapy.Field()
    # 论文在服务器上的路径，config中设置，不需爬取
    paperPath = scrapy.Field()
    # 论文下载url，因为下载会重定向，不会是paperurl
    paperPdfUrl = scrapy.Field()
    # 论文pdf提取结果，检索组已提供代码，直接调用即可
    paperContent = scrapy.Field()
    # 视频url
    videoUrl = scrapy.Field()
    # 视频下载url
    videoFileUrl = scrapy.Field()
    # 视频存在服务器上路径
    videoPath = scrapy.Field()
    # 视频提取内容结果
    videoContent = scrapy.Field()
    # 数据集链接，没有则不用管
    datasetUrl = scrapy.Field()


class PaperweeklyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    year = scrapy.Field()
    publisher = scrapy.Field()
    abstract = scrapy.Field()
    subjects = scrapy.Field()
    paperUrl = scrapy.Field()
    codeUrl = scrapy.Field()
    paperPath = scrapy.Field()
    #file_urls = scrapy.Field()
