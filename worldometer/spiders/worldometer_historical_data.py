import scrapy
from scrapy.crawler import CrawlerProcess
from multiprocessing import Process


class WorldometerSpider(scrapy.Spider):
    name = "worldometer_historical_data"
    allowed_domains = ["worldometers.info"]
    start_urls = [
        "https://www.worldometers.info/world-population/population-by-country/"]

    def parse(self, response):

        countries = response.xpath('//td/a')

        for country in countries:
            # (.//text()) continues on from every country's xpath
            country_name = country.xpath('.//text()').get()
            # link returns the relative link for the current country
            link = country.xpath('.//@href').get()

            yield response.follow(url=link, callback=self.parse_country, meta={'country': country_name})

    def parse_country(self, response):
        country = response.request.meta['country']

        rows = response.xpath(
            "(//table[@class='table table-striped table-bordered table-hover table-condensed table-list'])[1]/tbody/tr")

        for row in rows:
            # scrap data row by row
            year = row.xpath(".//td[1]/text()").get()
            population = row.xpath(".//td[2]/strong/text()").get()
            annual_change = row.xpath(".//td[4]/text()").get()
            migrants = row.xpath(".//td[5]/text()").get()
            median_age = row.xpath(".//td[6]/text()").get()
            population_density = row.xpath(".//td[8]/text()").get()
            urban_population = row.xpath(".//td[10]/text()").get()
            urban_pop_percent = row.xpath(".//td[9]/text()").get()

            # save to a local file in jsonlines format
            yield {
                'country': country,
                'year': year,
                'population': population.replace(",", ""),
                'annual_change': annual_change.replace(",", ""),
                'migrant_net': migrants.replace(",", ""),
                'median_age': median_age,
                'persons_per_square_km': population_density.replace(",", ""),
                'urban_population': urban_population.replace(",", ""),
                'percent_urban_population': urban_pop_percent.replace(" %", "")
            }


def crawl():
    '''initiates the crawler process for scraping worldometer'''
    process = CrawlerProcess()
    process.crawl(WorldometerSpider)
    process.start()

# If implemented as a google cloud functino


def op_process(target):
    '''To allow operation in the cloud.
    Args:
        target(func): The function to be called in Process.
    Returns:
        None
    TODO: Implement scrapy-bigquery to upload into big query'''

    main_process = Process(target=target)
    main_process.start()
    main_process.join()
    return


if __name__ == '__main__':
    '''for operation locally.'''
    crawl()
    op_process(target=crawl)
