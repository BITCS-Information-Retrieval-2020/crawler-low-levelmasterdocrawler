# -*- encoding: utf-8 -*-
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from crawler.spiders.arxiv_crawler import ArxivSpider
from crawler.spiders.acl_crawler import AclwebSpider
from crawler.spiders.papersWithCode_crawler import PapersWithCodeSpider
from crawler.spiders.paperweekly_crawler import PaperweeklyCrawlerSpider
from scrapy.utils.log import configure_logging
import yaml
import logging

logging_config_file = "./conf/logging_config.yaml"

# 设置日志
with open(logging_config_file, 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    f.close()
logger = logging.getLogger(__name__)


def main():
    with open('./conf/config.yaml', 'r', encoding="utf-8") as f:
        crawler_config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

    crawler_settings = Settings({
        "CONCURRENT_REQUESTS": crawler_config["CONCURRENT_REQUESTS"],
        "BOT_NAME": "crawler",
        "SPIDER_MODULES": ["crawler.spiders"],
        "NEWSPIDER_MODULE": "crawler.spiders",
        "ROBOTSTXT_OBEY": False,
        "ITEM_PIPELINES": crawler_config["ITEM_PIPELINES"],
        "FILES_STORE": crawler_config["FILES_STORE"],
        "DOWNLOAD_TIMEOUT": crawler_config["DOWNLOAD_TIMEOUT"],
        # arxiv unique settings
        # "DOWNLOADER_MIDDLEWARES": crawler_config["DOWNLOADER_MIDDLEWARES"],
        "COOKIES_ENABLED": crawler_config["COOKIES_ENABLED"],
        "RETRY_ENABLED": crawler_config["RETRY_ENABLED"],
        "RETRY_TIMES": crawler_config["RETRY_TIMES"],
        "USER_AGENT": crawler_config["USER_AGENT"]})
    runner = CrawlerRunner(crawler_settings)
    configure_logging(
        {
            "LOG_FORMAT": "%(message)s",
            "LOG_LEVEL": crawler_config["LOG_LEVEL"],
            "LOG_FILE": crawler_config["LOG_FILE"]
        }
    )
    d = runner.crawl(eval(crawler_config["SPIDER_TYPE"]))
    logger.info("Begin Crawler!")
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()
