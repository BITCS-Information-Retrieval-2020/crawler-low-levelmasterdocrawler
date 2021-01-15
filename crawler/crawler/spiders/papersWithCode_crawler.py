import scrapy
from crawler.items import CrawlerItem
from scrapy.selector import Selector

import logging
import yaml
logging_config_file = './conf/logging_config.yaml'

# 设置日志
with open(logging_config_file, 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()
logger = logging.getLogger(__name__)


class PapersWithCodeSpider(scrapy.Spider):

    name = 'papersWithCodeCrawler'
    allowed_domains = ['paperswithcode.com']
    start_urls = ['https://paperswithcode.com/sota']
    url_preflix = "https://paperswithcode.com"

    def parse(self, response):
        fields = response.css("h4 a::text").getall()
        # yield dict(zip(range(len(fields)), fields))
        next_pages = response.css("div.sota-all-tasks a::attr(href)").getall()
        for page in next_pages:
            next_page = response.urljoin(page)
            logger.info("1： " + next_page)
            yield scrapy.Request(next_page, callback=self.parse_subfields)
            logger.info("1完成 " + next_page)

    def parse_subfields(self, response):
        field = response.css("h1::text").get()
        subfields = response.css("h4::text").getall()
        # map(str.strip, subfields)
        for i in range(len(subfields)):
            subfields[i] = str(subfields[i]).strip()
        task_pages = response.css("div.sota-all-tasks a::attr(href)").getall()
        # mydict = { i : "" for i in subfields }
        c = 0
        for page in task_pages:
            next_page = response.urljoin(page)
            # request = scrapy.Request(next_page, callback=self.parse_tasks, meta = {"subfield": subfields[c]})
            logger.info("2： " + next_page)
            request = scrapy.Request(next_page, callback=self.parse_tasks)
            yield request
            logger.info("2完成 " + next_page)
            # mydict[subfields[c]]= {i : papers for i in tasks}
            c += 1

    # yield {"field" : field, "subfields" : dict(zip(range(len(subfields)), subfields))}
    # yield {field : subfields}

    def parse_tasks(self, response):
        # subfield = response.meta["subfield"]
        tasks = response.css("h1.card-title::text").getall()
        subtask_pages = response.css("div.card a::attr(href)").getall()
        c = 0
        for page in subtask_pages:
            next_page = response.urljoin(page)
            logger.info("3： " + next_page)
            # yield scrapy.Request(next_page, callback=self.parse_subtasks, meta = {"task": tasks[c]})
            yield scrapy.Request(next_page, callback=self.parse_subtasks)
            logger.info("3完成 " + next_page)
            c += 1

    # yield {"subfield" : subfield, "tasks" : dict(zip(range(len(tasks)), tasks))}

    def parse_subtasks(self, response):
        # task = response.meta["task"]
        subtasks = response.css("div:not(.text-center).paper a::text").getall()
        paper_pages = response.css(
            "div.text-center.paper a::attr(href)").getall()
        c = 0
        for page in paper_pages:
            next_page = response.urljoin(page)
            # yield scrapy.Request(next_page, callback=self.parse_abstracts, meta={"paper":subtasks[c]})
            logger.info("4： " + next_page)
            yield scrapy.Request(next_page, callback=self.parse_abstracts)
            logger.info("4完成" + next_page)
            c += 1

    # yield {"task" : task, "papers" : dict(zip(range(len(subtasks)), subtasks))}

    def parse_abstracts(self, response):
        # paper = response.meta["paper"]
        # title = response.xpath("/html[@class='hydrated']/body/div[@class='container']/div[@class='container content content-buffer']/div[@class='paper-title']/div[@class='row']/div[@class='col-md-12']/h1/text()")[0].extract()
        title = response.css("div.paper-title h1::text").get().strip()
        # title=response.css("div.paper-title::text").get()
        a1 = str(response.css("div.paper-abstract p::text").get()).strip()
        a2 = str(response.css("div.paper-abstract p span+span::text").get()).strip()
        abstract = a1 + a2
        # content = response.xpath(
        #     "/html[@class='hydrated']/body/div[@class='container']/div[@class='container content content-buffer']/div[@class='paper-title']/div[@class='row']/div[@class='col-md-12']/div[@class='authors']/p")
        # year=content.xpath("./span[@class='author-span'][1]/text()").extract()
        # year=response.css("span.author-span.xh-highlight::text").extract()
        date = response.css("div.authors span::text")[0].extract()
        dates = date.split(" ")
        year = dates[-1]
        authors = []
        # paper_url =response.xpath("/html[@class='hydrated']/body/div[@class='container']/div[@class='container content content-buffer']/div[@class='paper-abstract']/div[@class='row']/div[@class='col-md-12']/a[@class='badge badge-light']/@herf").extract()
        paper_urls = response.css(
            "div.paper-abstract a::attr(href)").extract()[1]
        paper_url = paper_urls.replace(".pdf", "")
        codeUrl = response.css(
            "div#id_paper_implementations_collapsed a::attr(href)").getall()
        publisher = response.css("span.item-conference-link a::text").get()
        writers = response.css("span.author-span a::text").getall()
        for writer in writers:
            name = writer.split(" ")
            first_name = name[0]
            last_name = " ".join(name[1:-1])
            authors.append({"firstName": first_name, "lastName": last_name})
        item = CrawlerItem()
        item["title"] = title
        item["_id"] = "".join(filter(str.isalnum, title)).lower()
        item["authors"] = authors
        item["year"] = year
        item["publisher"] = publisher
        item["abstract"] = abstract
        # item["_id"] = arxiv_id
        # item["subjects"] = subjects
        item["paperUrl"] = paper_url
        item["paperPdfUrl"] = paper_url + ".pdf#pdfjs.action=download"
        item["codeUrl"] = codeUrl

        return item
