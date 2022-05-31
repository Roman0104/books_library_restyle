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
    book_collection = "l55"
    link_collection = urljoin(url, book_collection)

    try:
        response = requests.get(link_collection)
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

    book_id = soup.find(id="content").find_all("table")[0].find("a")["href"]
    book_link = urljoin(url, book_id)

    print(book_link)

    logger.info(f"Ссылка на книгу {book_link}")


if __name__ == "__main__":
    main()
