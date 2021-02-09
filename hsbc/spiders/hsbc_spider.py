import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hsbc.items import Article


class hsbc_spiderSpider(scrapy.Spider):
    name = 'hsbc_spider'
    start_urls = ['https://www.hsbc.com/news-and-media/media-releases?page=1&take=20']

    def parse(self, response):
        links = response.xpath('//td//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="pagination__next hidden-xs"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//p[@class="link-to-author-page__date"]/text()').get().strip()
        date = datetime.strptime(date, '%d %b %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="sublayout article-sublayout "]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)


        return item.load_item()
