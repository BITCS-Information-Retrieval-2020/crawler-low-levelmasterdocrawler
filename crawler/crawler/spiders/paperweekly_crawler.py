import scrapy
import requests
from crawler.items import PaperweeklyItem


# cookie home
# _ga=GA1.2.1743015037.1609041231; _gid=GA1.2.1171315232.1609291887; _gat=1

# cookie arXiv
# _ga=GA1.2.1743015037.1609041231; _gid=GA1.2.1171315232.1609291887; _gat=1


class PaperweeklyCrawlerSpider(scrapy.Spider):
    name = 'paperweekly_crawler'
    allowed_domains = ['paperweekly.site', 'arxiv.org']
    base_url = 'http://www.paperweekly.site/arxiv/'
    # 'https://zijin.paperweekly.site/api/v1/arxiv_paper/'
    real_url = 'https://zijin.paperweekly.site/api/v1/arxiv_paper/'
    start_urls = [base_url]  # http://paperweekly.site/
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        + ' Chrome/87.0.4280.88 Safari/537.36',
        'Referer': 'http://www.paperweekly.site/',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InZ2bHZ2dSIsImVtYWlsIjoiNDUyMT'
                         + 'k1OTg2QHFxLmNvbSIsImV4cCI6MTkyNDc'
                         + '1NzY4NCwib3JpZ19pYXQiOjE2MDkzOTc2ODQsInVzZXJfaWQiOiJhN2E5ZTFh'
                         + 'NS0xOGYxLTQyZGMtYTE4My00YWNkOGY2YWE0NzAifQ.cS2WYuDbIPwyPxtPmWJ1xQLEXtFmlKzoCoxS7mmBnPM'
    }
    """
    def __init__(self):
        cook_dict = {}
        cook_dict['_ga'] = 'GA1.2.1743015037.1609041231'
        cook_dict['_gid'] = 'GA1.2.1171315232.1609291887'
        cook_dict['_gat'] = '1'

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.parse, cookies=self.cook_dict)
    """

    def parse(self, response):
        res = requests.get(self.real_url, headers=self.header)
        print(res.status_code)
        response_json = res.json()
        for paper in response_json['results']:
            yield scrapy.Request(paper["link"], callback=self.parse_paper)

        # for sel in response.xpath('/html/body/div[2]/div[1]/div/div[2]/div/div[@class="contain el-row"]'):
        #    paper_url = sel.xpath('./div[1]/div/div[1]/p/a/@href')[0].extract()
        #    yield scrapy.Request(paper_url, callback=self.parse_paper)

    def parse_paper(self, response):
        content = response.xpath(
            "/html/body[@class='with-cu-identity']/div[@class='flex-wrap-footer']/main/div[@id='content']/div[@id='ab"
            "s-outer']/div[@class='leftcolumn']/div[@id='content-inner']/div[@id='abs']"
        )
        title = content.xpath(
            "./h1[@class='title mathjax']/text()")[0].extract()
        abstract = content.xpath(
            "./blockquote[@class='abstract mathjax']/text()").extract()
        abstract = "".join(abstract).strip()

        authors = []
        for author in content.xpath("./div[@class='authors']/a"):
            name = author.xpath("./text()")[0].extract()
            name = name.split(" ")
            first_name = name[0]
            last_name = " ".join(name[1:-1])
            authors.append({"firstName": first_name, "lastName": last_name})
        publisher = "arxiv"
        arxiv_id = content.xpath(
            "./div[@class='metatable']/table//td[@class='tablecell arxivid']/span[@class='arxivid']/a/text()")[
            0].extract()
        subjects = content.xpath(
            "./div[@class='metatable']/table//td[@class='tablecell subjects']/span[@class='primary-subject']/text()")[
            0].extract()
        paper_url = response.xpath(
            "/html/body[@class='with-cu-identity']/div[@class='flex-wrap-footer']/main/div[@id='content']/div[@id='ab"
            "s-outer']/div[@class='extra-services']/div[@class='full-text']/ul//a[@class='abs-button download-p"
            "df']/@href")[0].extract()
        url_preflix = 'https://arxiv.org'
        paper_url = url_preflix + paper_url
        year = content.xpath("./div[@class='dateline']")[0].extract()

        item = PaperweeklyItem()
        item["_id"] = arxiv_id
        item["title"] = title
        item["year"] = year[-18:-7]
        item["publisher"] = publisher
        item["abstract"] = abstract
        item["subjects"] = subjects
        item["paperUrl"] = paper_url
        # file_urls = []
        # 注意爬取出来的paper_url不一定是可以直接下载的url，因为可能会重定向
        # file_urls.append(paper_url + ".pdf#pdfjs.action=download")
        # item["file_urls"] = file_urls
        yield item
