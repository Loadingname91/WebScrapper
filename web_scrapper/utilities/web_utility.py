import json
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

domains_supported = {
    'www.amazon.com': 'amazon',
    'www.flipkart.com': 'flipkart',
    'www.snapdeal.com': 'snapdeal',
    'www.ebay.com': 'ebay',
    'www.myntra.com': 'myntra',
}


def get_domain(url):
    domain = urlparse(url).netloc
    if domain in domains_supported:
        return domains_supported[domain]
    else:
        return None


def get_product_details(url):
    domain = get_domain(url)
    if domain:
        raw_response = requests.get(url)
        response = BeautifulSoup(raw_response.text, 'html.parser')
        return perform_scraping(url, response, domain)
    else:
        return None


def parsed_details(product_name, product_price, product_description, product_images, product_links, product_category,
                   product_features=None):
    return {
        "product": {
            'product_name': product_name,
            'product_price': product_price,
            'product_description': product_description,
            'product_features': product_features,
            'product_images': product_images,
            'product_category': product_category
        },
        'product_url': product_links,
    }


def amazon_scraping(response, url):
    product_name = response.find("span", {"id": "productTitle"}).text
    product_price = response.find("span", {"id": "priceblock_ourprice"}).text
    product_description = response.find("div", {"id": "productDescription"}).text
    product_features = response.find("div", {"id": "feature-bullets"}).text
    product_image = response.find("img", {"id": "landingImage"})['src']
    return parsed_details(product_name, product_price, product_description, product_image, url, "", product_features)


def extract_product_data(response, extract, tag, *args, **kwargs):
    if kwargs.get("findall") and kwargs.get("get"):
        data = response.findAll(tag, *args)[kwargs.get("get")]
    else:
        data = response.find(tag, *args)
    if data and extract in ["src"]:
        return data[extract]
    if data and hasattr(data, extract):
        return getattr(data, extract)
    else:
        return ""


def extract_table_contents(table):
    """Parses a html segment started with tag <table> followed
    by multiple <tr> (table rows) and inner <td> (table data) tags.
    It returns a list of rows with inner columns.
    Accepts only one <th> (table header/data) in the first row.
    """

    def rowget_data_text(tr, coltag='td'):  # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]

    rows = []
    trs = table.find_all('tr')
    headerow = rowget_data_text(trs[0], 'th')
    if headerow:  # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs:  # for every table row
        rows.append(rowget_data_text(tr, 'td'))  # data row
    return rows


def flipkart_scraping(soup, url):
    """
    This function scrapes the flipkart product page and returns the product details
    :param response:
    :param url:
    :return:
    """
    product_name = extract_product_data(soup, "text", "span", {"class": "B_NuCI"})
    product_price = extract_product_data(soup, "text", "div", {"class": "_30jeq3 _16Jk6d"})
    product_price = product_price.replace("₹", "")
    product_description = extract_product_data(soup, "text", "span", {"class": "B_NuCI"})
    # first attempt to get the product description
    containers = soup.find("div", {"class": "_3TOw5k"})
    feature_values = []
    if containers:
        for data in containers.findAll("div", {"class": "row"}):
            features = {}
            if data.name == "div" and data.get("class") == ["row"]:
                values = [i.text for i in data.children]
                if values[0] and values[1]:
                    features["feature_name"] = values[0]
                    features["feature_data"] = " ".join(values[1:])
                    feature_values.append(features)

    # second attempt to get the product features
    else:
        containers = soup.findAll("div", {"class": '_3dtsli'})
        if containers:
            for data in containers:
                features = {}
                if data.name == "div" and data.get("class") == ["_3dtsli"]:
                    _values = data.find(lambda tag: tag.name == 'table')
                    _parse_data = extract_table_contents(_values)
                    for _data in _parse_data:
                        features["feature_name"] = _data[0]
                        features["feature_data"] = _data[1]
                        feature_values.append(features)

    product_images = extract_product_data(soup, "src", "img", {"class": "_2r_T1I _396QI4"})
    if not product_images:
        product_images = extract_product_data(soup, "src", "img", {"class": "_396cs4 _2amPTt _3qGmMb"})
    product_category = extract_product_data(soup, "text", "a", {"class": "_2whKao"}, findall=True, get=2)
    return parsed_details(product_name, product_price, product_description, product_images, url, product_category,
                          json.dumps(feature_values))


def snapdeal_scraping(response, url):
    product_name = extract_product_data(response.find("div", {"class": "pdp-e-i-head"}), "h1", {"itemprop": "name"})
    product_price = extract_product_data(response.find("div", {"class": "payBlkBig"}), "span", {"itemprop": "price"})
    product_description = extract_product_data(response.find("div", {"class": "pdp-tabs"}), "div",
                                               {"class": "tabContent"})
    product_features = extract_product_data(response.find("div", {"class": "pdp-tabs"}), "div", {"class": "tabContent"})
    product_image = extract_product_data(response.find("div", {"class": "pdp-slider"}), "img", {"class": "cloudzoom"})
    return parsed_details(product_name, product_price, product_description, product_image, url, "", product_features)


def ebay_scraping(response, url):
    product_name = response.find("h1", {"id": "itemTitle"}).text
    product_price = response.find("span", {"id": "prcIsum"}).text
    product_description = response.find("div", {"id": "desc_div"}).text
    product_features = response.find("div", {"id": "desc_div"}).text
    product_image = response.find("img", {"id": "icImg"})['src']
    return parsed_details(product_name, product_price, product_description, product_image, url, "", product_features)


def myntra_scraping(response, url):
    product_name = response.find("h1", {"class": "pdp-name"}).text
    product_price = response.find("span", {"class": "pdp-price"}).text
    product_description = response.find("div", {"class": "pdp-description"}).text
    product_features = response.find("div", {"class": "pdp-description"}).text
    product_image = response.find("img", {"class": "pdp-image"})['src']
    return parsed_details(product_name, product_price, product_description, product_image, url, "", product_features)


def generic_scraping(response, url):
    # perform best effort scraping
    product_name = response.find("h1").text
    product_price = response.find("span").text
    product_description = response.find("div").text
    product_features = response.find("div").text
    product_image = response.find("img")['src']
    return parsed_details(product_name, product_price, product_description, product_image, url, "", product_features)


def perform_scraping(url, response, domain):
    if domain == 'amazon':
        return amazon_scraping(response, url)
    elif domain == 'flipkart':
        return flipkart_scraping(response, url)
    elif domain == 'snapdeal':
        return snapdeal_scraping(response, url)
    elif domain == 'ebay':
        return ebay_scraping(response, url)
    elif domain == 'myntra':
        return myntra_scraping(response, url)
    else:
        return generic_scraping(response, url)
