# -*- coding: utf-8 -*-
import scrapy


class AmazonItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    pid = scrapy.Field()
    price = scrapy.Field()
    stock_status = scrapy.Field()
    category = scrapy.Field()
    main_image = scrapy.Field()
    extra_images = scrapy.Field()
    description_text = scrapy.Field()
    description_html = scrapy.Field()
    product_specs = scrapy.Field()
    product_info = scrapy.Field()
    brand = scrapy.Field()
    seller = scrapy.Field()
    size = scrapy.Field()
    color = scrapy.Field()
    rating = scrapy.Field()
    reviews = scrapy.Field()
