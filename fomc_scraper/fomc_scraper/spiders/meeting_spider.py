import scrapy
import logging

class FomcSpider(scrapy.Spider):
    name = "meetings"
    start_urls = ['https://www.federalreserve.gov']
    def start_requests(self):

        urls = [
            'https://www.federalreserve.gov/monetarypolicy/fomc_historical_year.htm'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        year_links = response.xpath("//div[@id='article']//a/@href").getall()
        for year_link in year_links:
            yield response.follow(url=year_link, callback=self.year_parse)

    def year_parse(self, response):
        meeting_tables = response.xpath("//div[@id='article']/div")
        year = response.xpath("//div[@id='article']/h3/text()").get()

        for table in meeting_tables:
            response_data = {}
            response_data['year'] = year
            heading = table.xpath(".//h5/text()").get()
            if "Conference Call" in heading:
                response_data['event_type'] = "Conference Call"
            else:
                response_data['event_type'] = "Meeting"

            heading = heading.split(response_data['event_type'])[0].strip()
            if "-" in heading:
                response_data['multi_day'] = 1
                if "/" in heading:
                    response_data['start_month'] = heading.split('/')[0]
                    response_data['start_day'] = heading.split(" ")[1].split("-")[0]
                    response_data['end_month'] = heading.split("/")[1].split(" ")[0]
                    response_data['end_day'] = heading.split("-")[1]
                else:
                    response_data['start_month'] = heading.split(" ")[0]
                    response_data['start_day'] = heading.split(" ")[1].split("-")[0]
                    response_data['end_month'] = response_data['start_month']
                    response_data['end_day'] = heading.split("-")[1]
            else:
                response_data['multi-day'] = 0
                response_data['start_month'] = heading.split(" ")[0]
                response_data['start_day'] = heading.split(" ")[1]
                response_data['end_month'] = response_data['start_month']
                response_data['end_day'] = response_data['start_day']
            materials = table.xpath('.//p')

            for material in materials:
                ptext = material.xpath("./text()").get()
                if ptext and ptext.strip():
                    field_name = ptext.split(":")[0].split("(")[0].strip()
                    contents = material.xpath("./a/@href").getall()
                    if not contents:
                        content = ptext.split(":")[1].replace("\u00a0","").strip()

                    elif len(contents)>1:
                        links = []
                        for link in contents:
                            links.append(link.strip())
                        content = links
                    else:
                        content = contents[0]
                    response_data[field_name] = content
                else:
                    links = material.xpath("./a")

                    for link in links:
                        field_name = link.xpath("./text()").get().split("(")[0].strip()
                        response_data[field_name] = link.xpath("./@href").get()

            yield response_data