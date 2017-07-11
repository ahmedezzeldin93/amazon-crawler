# -*- coding: utf-8 -*-

import logging
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, settings, user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101"
                                            " Firefox/54.0"):
        super(RandomUserAgentMiddleware, self).__init__()
        self.user_agent = user_agent
        try:
            self.user_agent_engine = UserAgent()
        except Exception, ex:
            logging.error("Failed to create user agent engine object. Reason: %s", ex)

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)
        crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
        return obj

    def process_request(self, request, spider):
        try:
            user_agent = self.user_agent_engine.random
        except Exception, ex:
            logging.error("Failed to get the automatic user agent. Reason: %s", ex)
            user_agent = self.user_agent
        logging.info("[R2D2] Using user agent (%s)", user_agent)
        request.headers.setdefault('User-Agent', user_agent)