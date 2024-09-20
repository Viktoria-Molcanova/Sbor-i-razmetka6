import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from urllib.parse import urljoin

from unsplash.items import ImageItem


class UnsplashSpider(scrapy.Spider):
    name = "UnsplashSpider"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com/t/"]

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//article[@class='product_pod']"), callback="parse_item", follow=True),
    )

    def parse(self, response, **kwargs):

        loader = ItemLoader(item=ImageItem(), response=response)
        loader.default_input_processor = MapCompose(str.strip)

        loader.add_xpath("image_urls", "//img[@srcset]/@srcset")
        loader.add_xpath("title", "//h1/text()")
        loader.add_xpath("category", "//a[starts-with(@href, '/t/')]/text()")
        loader.add_xpath("image_urls", "//div[@class='item active']/img/@src")
        half_image_link = response.xpath("//div[@class='item active']/img/@src").getall()
        image_link = [urljoin("https://unsplash.com/t/", img_url) for img_url in half_image_link]

        loader.add_value("image_urls", image_link)

        yield loader.load_item()
