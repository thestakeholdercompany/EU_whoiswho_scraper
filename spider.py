import re
import scrapy

# Scrapy spider to crawl and scrape all persons from the EU Whoiswho
# website: http://europa.eu/whoiswho/public/


class EUSpider(scrapy.Spider):
    name = 'euspider'
    # Crawl the website using its 'hierarchy' structure
    start_urls = ['http://europa.eu/whoiswho/public/index.cfm?fuseaction=idea.hierarchy&lang=en']

    # Be nice, wait 0.5 seconds between URLs downloads (will take
    # roughly 9 hours to retrieve all pages)
    custom_settings = {'DOWNLOAD_DELAY': 0.5}

    # Process the retrieved webpage
    def parse(self, response):

        if response.xpath('//table[@id="person-detail"]'):
            # scrape_people(response)
            # Retrieve hiararchy/breadcrumb
            hierarchy = response.xpath('//span[@itemtype="http://data-vocabulary.org/Breadcrumb"]//text()').extract()

            # Remove empty items in the list
            hierarchy = [item for item in hierarchy if item.strip()]

            # Strip first item ('institution') and last item ('name of person')
            hierarchy = hierarchy[1:-1]

            person_table = response.xpath('//table[@id="person-detail"]')

            person_data = person_table.xpath('.//hr/../preceding-sibling::*')

            # Retrieve telephone number(s)
            telephone = person_data.xpath('.//span[@itemprop="telephone"]/text()').extract()

            # Strip whitespace from telephone number items
            telephone = [item.strip() for item in telephone]

            # Sometimes extra telephone numbers are placed under a 'p' tag
            possible_extra_phones = person_data.xpath('.//p/text()').extract()
            if possible_extra_phones:
                for item in possible_extra_phones:
                    if re.search('Tel:', item):
                        item = re.sub('Tel:', '', item).strip()
                        telephone.append(item)

            # Retrieve email and/or URL
            hrefs = person_data.xpath('.//a/@href').extract()
            url = ''
            email = ''
            for href in hrefs:
                if re.search('^mailto:', href):
                    email = href[7:]
                else:
                    url = href

            # Retrieve name, title and fax and yield it together with
            # the other results
            s = ",";
            address = person_data.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()
            postcode = person_data.xpath('.//span[@itemprop="postalCode"]/text()').extract_first()
            locality = person_data.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()
            yield {
                'name': response.css('h3::text').extract_first(),
                'title': response.xpath('//td[@itemprop="jobTitle"]/text()').extract_first(),
                'telephone': telephone,
                'fax': person_data.xpath('.//span[@itemprop="faxNumber"]/text()').extract_first(),
                'email': email,
                'address': address if address is not None else "",
                'postcode': postcode.replace(" ", "") if postcode is not None else "",
                'locality': locality.replace('\t', '').replace('\n', '').replace(" ", "") if locality is not None else "",
                'url': url,
                'hierarchy': hierarchy,
                'source': response.url
            }

        # if response.xpath("//meta[@name='DCSEXT.W_INSTITUTION']") !=  "List of institutions \r\n" :
        #     # scrape_org(response)
        #     print("foo")


    def scrape_people(response):
        # Retrieve hiararchy/breadcrumb
        hierarchy = response.xpath('//span[@itemtype="http://data-vocabulary.org/Breadcrumb"]//text()').extract()

        # Remove empty items in the list
        hierarchy = [item for item in hierarchy if item.strip()]

        # Strip first item ('institution') and last item ('name of person')
        hierarchy = hierarchy[1:-1]

        person_table = response.xpath('//table[@id="person-detail"]')

        person_data = person_table.xpath('.//hr/../preceding-sibling::*')

        # Retrieve telephone number(s)
        telephone = person_data.xpath('.//span[@itemprop="telephone"]/text()').extract()

        # Strip whitespace from telephone number items
        telephone = [item.strip() for item in telephone]

        # Sometimes extra telephone numbers are placed under a 'p' tag
        possible_extra_phones = person_data.xpath('.//p/text()').extract()
        if possible_extra_phones:
            for item in possible_extra_phones:
                if re.search('Tel:', item):
                    item = re.sub('Tel:', '', item).strip()
                    telephone.append(item)

        # Retrieve email and/or URL
        hrefs = person_data.xpath('.//a/@href').extract()
        url = ''
        email = ''
        for href in hrefs:
            if re.search('^mailto:', href):
                email = href[7:]
            else:
                url = href

        # Retrieve name, title and fax and yield it together with
        # the other results
        s = ",";
        address = person_data.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()
        postcode = person_data.xpath('.//span[@itemprop="postalCode"]/text()').extract_first()
        locality = person_data.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()
        yield {
            'name': response.css('h3::text').extract_first(),
            'title': response.xpath('//td[@itemprop="jobTitle"]/text()').extract_first(),
            'telephone': telephone,
            'fax': person_data.xpath('.//span[@itemprop="faxNumber"]/text()').extract_first(),
            'email': email,
            'address': address if address is not None else "",
            'postcode': postcode.replace(" ", "") if postcode is not None else "",
            'locality': locality.replace('\t', '').replace('\n', '').replace(" ", "") if locality is not None else "",
            'url': url,
            'hierarchy': hierarchy,
            'source': response.url
        }

        # Check if this webpage has any other hierarchy URLs, if so then
    # send them to Scrapy to continue crawling and scraping them
        for url in response.xpath('//table[@id="mainContent"]//ul//a/@href').extract():
            matching = re.match('.*index\.cfm\?fuseaction=idea\.hierarchy&nodeID=.*', url)
            if matching:
                print(matching, url)
                yield scrapy.Request(response.urljoin(url))


    def scrape_org(self, response):
        meta_name = response.xpath("//meta[@name='DCSEXT.W_INSTITUTION']/@content")[0].extract()
        print("============================================================")
        print("============================================================")
        print(meta_name)
        print("============================================================")
        print("============================================================")
        # if response.xpath("//*[contains(text(), 'W_INSTITUTION')]"):
        #     print(response.xpath("//*[contains(text(), 'W_INSTITUTION')]"))
        # Retrieve hiararchy/breadcrumb
        hierarchy = response.xpath('//span[@itemtype="http://data-vocabulary.org/Breadcrumb"]//text()').extract()
        # Remove empty items in the list
        hierarchy = [item for item in hierarchy if item.strip()]
        # Strip first item ('institution') and last item ('name of person')
        hierarchy = hierarchy[1:-1]
        print("hierarchyhierarchyhierarchyhierarchyhierarchyhierarchy")
        print(hierarchy)
        print("============================================================")

        org_table = response.xpath("//meta[@name='DCSEXT.W_INSTITUTION']")
        print("org_tableorg_tableorg_tableorg_tableorg_tableorg_table")
        print(org_table)
        print("============================================================")

        org_data = org_table.xpath('.//hr/../preceding-sibling::*')

        # Retrieve telephone number(s)
        telephone = org_data.xpath('.//span[@itemprop="telephone"]/text()').extract()
        print("telephonetelephonetelephonetelephonetelephonetelephone")
        print(telephone)
        print("============================================================")

        # Retrieve name, title and fax and yield it together with
        # the other results
        s = ",";
        address = org_data.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first()
        postcode = org_data.xpath('.//span[@itemprop="postalCode"]/text()').extract_first()
        locality = org_data.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first()
