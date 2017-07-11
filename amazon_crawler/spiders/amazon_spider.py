# -*- coding: utf-8 -*-
import re

from scrapy.spiders.crawl import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from amazon_crawler.items import AmazonItem


class AmazonSpiderSpider(CrawlSpider):
    name = 'amazon_spider'

    allowed_domains = ['amazon.com']
    start_urls = ['https://www.amazon.com/dp/B06X9VSZYM/']

    RESTRICT_XPATH_ELECTRONICS = '//h3[contains(text(),"Electronics, Computers & Office")]/following-sibling::*/a'

    RESTRICT_XPATH_SUBCATEGORY= ['//div[@class="left_nav browseBox"]/h3[contains(text(),"Featured")]/following-sibling::ul[1]/li/a',
                                 '//div[contains(@id, "categoryTiles")]/descendant::ol/descendant::a',
                                 '//div[@id="nav-subnav"]/descendant::a',
                                 '//div[@id="atfResults"]/descendant::a',
                                 '//div[@id="pagn"]/descendant::a']

    rules = [
        Rule(LinkExtractor(allow=r'(dp/\w+)',deny=(r'product\-reviews',r'offer\-listing'), unique=False),
                 callback='parse_item', follow=False),
        Rule(LinkExtractor(restrict_xpaths=RESTRICT_XPATH_ELECTRONICS, unique=True), follow=True),
        Rule(LinkExtractor(restrict_xpaths=RESTRICT_XPATH_SUBCATEGORY, unique=True), follow=True)
    ]


    def parse_category(self, response):
        self.logger.info(response.css('.fsdDeptCol a').extract())


    def parse_item(self, response):
        self.logger.info("Parsing product page %s", response.url)
        amazon_item = AmazonItem()
        initialize_item(item_fields=amazon_item.fields, item=amazon_item)
        item_populated = populate_item(response, amazon_item)
        return item_populated


def initialize_item(item_fields, item):
    for field in item_fields:
        item[field] = u''
    return item


def populate_item(response, item):
    item['url'] = response.url
    item['title'] = response.css('#centerCol h1 span#productTitle').xpath('normalize-space(text())').extract()
    item['pid'] =  re.findall(r'/dp/(\w+)', response.url)
    item['price'] = get_price(response)
    item['stock_status'] = response.css('#availability span').xpath('normalize-space(text())').re('[a-zA-Z\s]+')
    item['main_image'] = response.css('#main-image-container #landingImage').xpath('@data-old-hires').extract()
    item['category'] = response.css('#wayfinding-breadcrumbs_container ul li a').xpath('normalize-space(text())').extract()[:-1]
    item['rating']  = response.css('#centerCol #averageCustomerReviews .a-declarative .reviewCountTextLinkedHistogram').xpath('@title').re(r'^(\d.\d).*')
    item['brand'] = response.css('#centerCol #bylineInfo').xpath('text()').extract()
    item['description_text'] = response.css('#productDescription p').xpath('normalize-space(string())').extract()
    item['seller'] = response.css('#merchant-info').xpath('normalize-space(text())').re('by (.*)\.')
    item['size'] = response.css('#variation_size_name span.selection').xpath('normalize-space(text())').extract()
    item['color'] = response.css('#variation_color_name span.selection').xpath('normalize-space(text())').extract()
    item['product_specs'] = get_product_specs(response)
    item['reviews'] = get_reviews(response)
    item['product_info'] = get_product_info(response)
    return item


def get_price(response):
    digits = response.css('#centerCol #price #priceblock_ourprice').xpath('text()').re('\d')
    if digits:
        return float(''.join(digits))
    else:
        return None


def get_reviews(response):
    reviews_titles = response.css('.reviews-content .a-section.review .review-title').xpath('text()').extract()
    reviews_ratings = response.css('.reviews-content .a-section.review .review-rating span').xpath('text()').re(r'^(\d.\d).*')
    reviews_text =response.css('.reviews-content .a-section.review .review-data .review-text .a-expander-content')\
        .xpath('string()').extract()
    reviews_data = [{reviews_titles[i], reviews_ratings[i], ''.join(reviews_text[i])} for i in range(len(reviews_titles))]
    return reviews_data


def get_product_specs(response):
    spec_list = response.css('table#productDetails_techSpec_section_1 th, table#productDetails_techSpec_section_1 td')\
        .xpath('normalize-space(text())').extract()
    return zip(spec_list[::2], spec_list[1::2])


def get_product_info(response):
    info_list = response.css('#productDetails_detailBullets_sections1 th, #productDetails_detailBullets_sections1 td')\
        .xpath('normalize-space(text())').extract()
    return zip(info_list[::2], info_list[1::2])
