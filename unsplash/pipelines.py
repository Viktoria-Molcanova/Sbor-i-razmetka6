# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import hashlib
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class CustomImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item.get('image_urls', []):
            if image_url:
                yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image_paths'] = image_paths
        return item


class CsvExportPipeline:
    def __init__(self):
        self.file = None
        self.writer = None

    def open_spider(self, spider):
        self.file = open('images_info.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Image URL', 'Local Path', 'Title', 'Category'])

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for path in item.get('image_paths', []):
            self.writer.writerow([
                item['image_urls'][0] if item['image_urls'] else None,
                path,
                item.get('title', ''),
                item.get('category', '')
            ])
        return item


class ImageName(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(request.url.encode()).hexdigest()
        return f"{item['image_urls'][0]} - {image_guid}.jpg"
