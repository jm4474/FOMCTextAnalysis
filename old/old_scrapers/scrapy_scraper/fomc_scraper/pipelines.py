# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import logging

class FomcScraperPipeline(object):
    def process_item(self, item, spider):
        return item

class CsvWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('meeting_metadata.csv', 'w', newline='')
        self.items = []
        self.colnames = []

    def close_spider(self, spider):
        csvWriter = csv.DictWriter(self.file, fieldnames = self.colnames)#, delimiter=',')
        logging.info("HEADER: " + str(self.colnames))
        csvWriter.writeheader()
        for item in self.items:
            csvWriter.writerow(item)
        self.file.close()

    def process_item(self, item, spider):
        # add the new fields
        for f in item.keys():
            if f not in self.colnames:
                self.colnames.append(f)

        # add the item itself to the list
        self.items.append(item)
        return item