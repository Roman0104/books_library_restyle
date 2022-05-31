import logging
import sys
import time
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


def main() -> None:
    logger = logging.getLogger("parse_tululu_category")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("parse_tululu_category.log",
                                       mode='w',
                                       encoding='utf-8', )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    url = "https://tululu.org/"
    book_category = "/l55/"
    link_category = urljoin(url, book_category)

    for page in range(1, 11):
        link_category_page = urljoin(link_category, str(page))

        try:
            response = requests.get(link_category_page)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            sys.stderr.write(f"Ошибка соединения\n")
            logger.error(f"Ошибка соединения")
            time.sleep(3)
            return
        except requests.exceptions.HTTPError:
            sys.stderr.write(f"Ошибка на странице\n")
            logger.error(f"Ошибка на странице")
            return

        soup = BeautifulSoup(response.text, "lxml")
        parse_content_table = soup.find(id="content").find_all("table")

        for book in parse_content_table:
            print(urljoin(url, book.find("a")["href"]))
            logger.info(f'Страница {page} ссылка: {urljoin(url, book.find("a")["href"])}')

        logger.info(f"Парсер успешно распарсил страницу {page}")

    logger.info(f"Парсер успешно завершил работу")


if __name__ == "__main__":
    main()
