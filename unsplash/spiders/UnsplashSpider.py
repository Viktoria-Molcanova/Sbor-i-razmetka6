import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose
from unsplash.items import ImageItem
from urllib.parse import urljoin


import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from urllib.parse import urljoin


class UnsplashSpider(scrapy.Spider):
    name = "UnsplashSpider"
    allowed_domains = ["unsplash.com"]
    start_urls = ["https://unsplash.com/t/"]

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//article[@class='product_pod']"), callback="parse_item", follow=True),
    )

    def parse(self, response, **kwargs):
        try:
            loader = ItemLoader(item=ImageItem(), response=response)
            loader.default_input_processor = MapCompose(str.strip)

            loader.add_xpath("image_urls", "//img[@srcset]/@srcset")
            loader.add_xpath("title", "//h1/text()")
            loader.add_xpath("category", "//a[starts-with(@href, '/t/')]/text()")


            half_image_link = response.xpath("//img[@srcset]/@srcset").getall()
            if not half_image_link:
                self.logger.warning("Не удалось найти изображения на странице.")
                return

            image_link = [urljoin("https://unsplash.com/t/", img_url) for img_url in half_image_link]
            loader.add_value("image_urls", image_link)

            yield loader.load_item()

        except Exception as e:
            self.logger.error(f"Ошибка при обработке страницы {response.url}: {e}")