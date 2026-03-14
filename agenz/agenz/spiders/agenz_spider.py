import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor


class AgenzSpiderSpider(scrapy.Spider):
    name = "agenz-spider"
    allowed_domains = ["agenz.ma"]
    start_urls = []
    # for city_name in ["casablnca"]:
    for i in range(4):
        start_urls.append(
            f"https://agenz.ma/fr/list.htm??page={i}&prixmax=9500000&type=villa&province=kenitra&lat=33.571298877886946&lng=-7.537391991925659&address=sale&transaction_type=vente"
            # f"https://agenz.ma/fr/list.htm??page={i}&prixmax=9500000&type=appartement&province=kenitra&lat=33.571298877886946&lng=-7.537391991925659&address=sale&transaction_type=location"
        )
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    }

    rules = (Rule(LinkExtractor(allow="")),)

    custom_settings = {"DEFAULT_REQUEST_HEADERS": headers}

    def parse(self, response):
        # 1. Select the INDIVIDUAL cards (notice the change from listListingCards to listingCard)
        cards = response.xpath('//div[contains(@class, "_listingCard_")]')
        for card in cards:
            # 2. Extract the location text using a relative path
            raw_title_parts = card.xpath(
                './/a[contains(@class, "_locationAdress_")]//text()'
            ).getall()

            # 2. Join and clean the text
            # result: "villa à vendre casablanca - Hay Riad"
            full_title = " ".join([t.strip() for t in raw_title_parts if t.strip()])
            title = card.xpath(
                './/a[contains(@class, "_locationAdress_")]/span/text()'
            ).get()
            # Extract the price value (e.g., "22 000" or "1 770 000")
            price = card.xpath('.//*[contains(@class, "_nouveau_")]/text()').get()

            # Clean the data: remove non-breaking spaces (\xa0) and extra whitespace
            if price:
                price = price.replace("\xa0", "").strip()
            # price = card.xpath(
            #     './/p[contains(@class, "_price_")]/span[contains(@class, "_nouveau_")]/text()'
            # ).get() # price for sales listing
            surface = card.xpath(
                './/div[@data-highlight="surface"]//span[contains(@class, "_highlightValue_")]/text()'
            ).get()
            creation_date = card.xpath(
                './/div[contains(@class, "_dateCreationList_")]/text()'
            ).get()
            district = title.split("-")[-1].strip()
            relative_url = card.xpath("./@data-url").get()
            if title:
                # 2. Split by the hyphen and take the first part
                # .split('-')[0] gives "Casablanca "
                # .strip() removes the trailing space to give "Casablanca"
                city = title.split("-")[0].strip()
            else:
                city = None
            # 2. Build the complete URL
            # You can join it with the base domain
            if relative_url:
                complete_url = f"https://agenz.ma{relative_url}"
            else:
                complete_url = None
            if district:
                district = district.lower()
                district = district.replace("quartier", "").replace("des", "").strip()
                # Replace French accented characters with normal characters
                district = (
                    district.replace("é", "e").replace("è", "e").replace("ê", "e")
                )
                district = district.replace("à", "a").replace("â", "a")
                district = district.replace("ô", "o").replace("ö", "o")
                district = district.replace("î", "i").replace("ï", "i")
                district = district.replace("û", "u").replace("ü", "u")
                district = district.replace("ç", "c")
                district = district.replace("ñ", "n")
                # Clean up any extra spaces that might be left
                district = " ".join(district.split())

            # 3. Yield the data
            if title:
                yield {
                    "url": complete_url,
                    "city": city,
                    # "property_type": "villa",
                    "title": "".join(raw_title_parts),
                    "surface": surface.strip() if surface else None,
                    "price": price.strip() if price else None,
                    "age": creation_date.strip() if creation_date else None,
                    "quartier": district.strip() if district else None,
                }
