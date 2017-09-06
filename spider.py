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
        # If the webpage contains a table with id 'person-detail' then
        # get the person's data from it. Note that a webpage can contain
        # both the details of a person and further links in the
        # hierarchy which we should crawl, e.g.
        # http://europa.eu/whoiswho/public/index.cfm?fuseaction=idea.hierarchy&nodeID=370629&lang=en
        if response.xpath('//table[@id="person-detail"]'):
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
            yield {
                'name': response.css('h3::text').extract_first(),
                'title': response.xpath('//td[@itemprop="jobTitle"]/text()').extract_first(),
                'telephone': telephone,
                'fax': person_data.xpath('.//span[@itemprop="faxNumber"]/text()').extract_first(),
                'email': email,
                'url': url,
                'hierarchy': hierarchy,
                'source': response.url,
                'last_updated':person_data.xpath("//p[@class='dateupdate']//text()").extract_first().replace("Last update: ", "")
            }

        if response.xpath("//meta[@name='DCSEXT.W_INSTITUTION']") :

            org_name = response.xpath('.//h3[@itemprop="name"]/text()').extract()
            org_address = response.xpath('.//span[@itemprop="streetAddress"]/text()').extract()
            org_postal_code = response.xpath('.//span[@itemprop="postalCode"]/text()').extract()
            org_locality = response.xpath('.//span[@itemprop="addressLocality"]/text()').extract()

            # Retrieve email and/or URL
            hrefs = response.xpath('.//a/@href').extract()
            url = ''
            org_email = ''
            for href in hrefs:
                if re.search('^mailto:', href):
                    org_email = href[7:]
                else:
                    url = href

            # Retrieve telephone number(s)
            org_telephone = response.xpath('.//span[@itemprop="telephone"]/text()').extract()
            # Strip whitespace from telephone number items
            org_telephone = [item.strip() for item in org_telephone]
            # Sometimes extra telephone numbers are placed under a 'p' tag
            possible_extra_phones = response.xpath('.//p/text()').extract()
            if possible_extra_phones:
                for item in possible_extra_phones:
                    if re.search('Tel:', item):
                        item = re.sub('Tel:', '', item).strip()
                        org_telephone.append(item)

            # Retrieve hiararchy/breadcrumb
            org_hierarchy = response.xpath('//span[@itemtype="http://data-vocabulary.org/Breadcrumb"]//text()').extract()
            # Remove empty items in the list
            org_hierarchy = [item for item in org_hierarchy if item.strip()]
            # Strip first item ('institution') and last item ('name of person')
            org_hierarchy = org_hierarchy[1:-1]

            yield {
                'org_name': org_name,
                'address': org_address,
                'pincode': org_postal_code,
                'telephone': org_telephone,
                'fax': response.xpath('.//span[@itemprop="faxNumber"]/text()').extract_first(),
                'email': org_email,
                'url': org_email,
                'hierarchy': org_hierarchy,
                'source': response.url
            }


        # Check if this webpage has any other hierarchy URLs, if so then
        # send them to Scrapy to continue crawling and scraping them
        for url in response.xpath('//table[@id="mainContent"]//ul//a/@href').extract():
            matching = re.match('.*index\.cfm\?fuseaction=idea\.hierarchy&nodeID=.*', url)
            if matching:
                print(matching, url)
                yield scrapy.Request(response.urljoin(url))
