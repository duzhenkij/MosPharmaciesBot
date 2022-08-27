import requests
from bs4 import BeautifulSoup
import re


class Parser:

    def __init__(self, user_query: str):
        self.user_query = user_query
        self.regex_words = r'([Тт]аблетки| [Рр]аствор| [Пп]орошок| [Сс]прей| [Сс]редство| [Кк]апли| [Кк]апсулы| ' \
                           r'[Кк]рем| [Гг]ель| [Кк]рем-| [Мм]армелад| [Кк]онцентрат| [Кк]апм| [Пп]астилки| капс.|  ' \
                           r'капс| [Тт]абл.| [Гг]ранулы| [Сс]успензия| [Сс]уппозитории| таб| р-р| пор| [Гг]ран| ' \
                           r'[Сс]ироп| [Сс]прей | [Сс]редство| [Сс]упп| [Кк]апс| [Кк]апс.| [Сс]вечи| [Пп]рокладки| ' \
                           r'[Пп]одгузники| [Пп]омада| [Мм]асло| [Шш]ампунь| [Мм]аска| [Лл]ак)'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/'
                      'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
        }

    def parse_pharmacy_36_6(self):
        url = 'https://366.ru/search'
        payload = {'q': self.user_query, 'sort': 'price-asc'}
        r = requests.get(url, params=payload, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        goods = soup.find_all('a', class_='listing_product__title')
        goods_prices = soup.find_all('span', class_='price')

        titles = []
        dosages = []
        prices = []

        for i in range(0, len(goods)):
            item = goods[i].text.strip()
            price = goods_prices[i].text.strip().replace('₽', '').replace(' ', '').replace('\xa0', '')

            title_and_dosage_separated = re.split(self.regex_words, item)
            title = title_and_dosage_separated[0].strip()
            try:
                dosage = (title_and_dosage_separated[1] + title_and_dosage_separated[2]).strip()
            except IndexError:
                dosage = None

            titles.append(title)
            dosages.append(dosage)
            prices.append(price.replace(' ', ''))
        return titles, dosages, prices

    def parse_gorzdrav(self):
        url = 'https://gorzdrav.org/search/'
        payload = {'text': self.user_query}
        r = requests.get(url, params=payload, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        goods = soup.find_all('div', class_='c-prod-item__title')
        goods_prices = soup.find_all('span', class_='b-price')

        titles = []
        dosages = []
        prices = []

        for i in range(0, len(goods)):
            item = goods[i].text.strip()
            price = goods_prices[i].text.strip().replace('₽', '').replace(' ', '').replace('\xa0', '')

            title_and_dosage_separated = re.split(self.regex_words, item)
            title = title_and_dosage_separated[0].strip()
            try:
                dosage = (title_and_dosage_separated[1] + title_and_dosage_separated[2]).strip()
            except IndexError:
                dosage = None

            titles.append(title)
            dosages.append(dosage)
            prices.append(price)

        return titles, dosages, prices

    def parse_samson_pharma(self):
        url = 'https://samson-pharma.ru/catalog/'
        payloads = {'q': self.user_query}
        r = requests.post(url, params=payloads, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        goods = soup.find_all('a', class_='product-card__title')
        goods_prices = soup.find_all('div', class_='price_cnt')

        titles = []
        dosages = []
        prices = []

        for i in range(0, len(goods)):

            item = goods[i].find('span').text

            try:
                price = goods_prices[i].find('span', itemprop='price').\
                    text.\
                    strip().\
                    replace('₽', '').\
                    replace(' ', '').\
                    replace('\xa0', '')
            except AttributeError:
                price = None
            except IndexError:
                price = None

            try:
                prices.append(price)
            except IndexError:
                prices.append(None)

            title_and_dosage_separated = re.split(self.regex_words, item)
            title = title_and_dosage_separated[0]
            try:
                dosage = title_and_dosage_separated[1].lstrip() + title_and_dosage_separated[2]
            except IndexError:
                dosage = None

            titles.append(title)
            dosages.append(dosage)

        return titles, dosages, prices

    def parse_zdorov_ru(self):
        url = 'https://zdorov.ru/_next/data/eGyP-nbwxDHvptGHJ3H2g/catalog/search.json'
        payloads = {'q': self.user_query}
        r = requests.get(url, params=payloads)
        json_text = r.json()

        goods = json_text.get('pageProps').get('initialReduxState').get('catalog').get('goods')

        titles = []
        dosages = []
        prices = []

        for i in range(0, len(goods)):
            titles.append(goods[i].get('webData').get('drugTitle'))
            dosages.append(goods[i].get('webData').get('outFormTitle'))
            prices.append(goods[i].get('minPrice').get('normal'))

        return titles, dosages, prices

    def parse_stolichki(self):
        url = 'https://stolichki.ru/search'
        payloads = {'name': self.user_query}
        r = requests.get(url, params=payloads)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.find_all('div', class_='product-info d-flex-class')

        titles = []
        dosages = []
        prices = []

        for item in items:

            goods = item.find('p', class_='product-title').text.strip()
            price = item.find('p', class_='product-price').\
                text.\
                strip().\
                replace('₽', '').\
                replace(' ', '').\
                replace('\xa0', '')

            title_and_dosage_separated = re.split(self.regex_words, goods)

            title = title_and_dosage_separated[0].strip()
            try:
                dosage = (title_and_dosage_separated[1] + title_and_dosage_separated[2]).strip()
            except IndexError:
                dosage = None

            titles.append(title)
            dosages.append(dosage)
            prices.append(price)

        return titles, dosages, prices
