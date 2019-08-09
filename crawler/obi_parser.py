from components import Parser, ParseResult
from bs4 import BeautifulSoup

class ObiParser(Parser):
    def parse(self, link: str, html: str):
        bs = BeautifulSoup(html, 'html.parser')

        pr = ParseResult([], None)

        try:
            for a_tag in bs.find_all('a'):
                url = a_tag.get('href')
                pr.links.append(url)

            if '/p/' in link:
                prod_id = int(link[link.rfind('/')+1:-1])
                name = bs.h1.get_text()
                image_link = bs.find(
                    'img', title=name
                )['src']
                price = bs.find('strong', itemprop='price').get_text()

                pr.product = {
                    'prod_id': prod_id,
                    'name': name,
                    'image_link': image_link,
                    'price': price
                }
        except:
            pr = ParseResult([], None)
            print(f'bad parse at {link}')

        return pr
