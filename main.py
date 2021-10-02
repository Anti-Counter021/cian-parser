import logging

import bs4
import requests


class ParserCian:

    def __init__(self, url: str):
        self._session: requests.Session = requests.Session()
        self._session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'ru',
        }
        self._url = url
        self._result = []

    def load_page(self):
        response = self._session.get(self._url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        containers = soup.select('article[data-name="CardComponent"]')
        for card in containers:
            self.parse_card(card)

    def parse_card(self, card: bs4.Tag):
        subtitle = card.select_one('span[data-mark="OfferSubtitle"]')
        title = card.select_one('div[data-name="TitleComponent"]')
        if not subtitle:
            rooms, square, floor = title.text.split(', ')
        else:
            rooms, square, floor = subtitle.text.split(', ')

        address_block = card.select_one('div._93444fe79c--labels--1J6M3')
        if not address_block:
            logging.error('Address not found')
            return
        address = ''
        for i in address_block:
            address += i.text

        price_block = card.select_one('span[data-mark="MainPrice"] > span')
        if not price_block:
            logging.error('Price not found')
            return
        price = price_block.text

        author_id_block = card.select_one('[data-name="AgentTitle"]')
        if not author_id_block:
            logging.error('Author ID not found')
            return
        author_id = author_id_block.text

        link_block = card.select_one('a._93444fe79c--link--39cNw')
        if not link_block:
            logging.error('Link not found')
            return
        link = link_block.get('href')

        self._result.append(
            {
                'rooms': rooms,
                'square': square,
                'floor': floor,
                'address': address,
                'price': price,
                'author_id': author_id,
                'url': link,
                'phone': self.parse_phone(link),
            }
        )

    def parse_phone(self, url: str):
        response = self._session.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        text = response.text

        soup = bs4.BeautifulSoup(text, 'lxml')
        phone_block = soup.select_one('a.a10a3f92e9--phone--3XYRR')
        if not phone_block:
            logging.error('Phone not found')
            return
        phone = phone_block.text
        return phone

    def run(self):
        page = self.load_page()
        self.parse_page(page)
        logging.info('Success!')
        return self._result


if __name__ == '__main__':
    cian = ParserCian('https://www.cian.ru/snyat-kvartiru/')
    print(cian.run())
