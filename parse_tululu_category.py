import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def parse_book_page(html_content) -> dict:

    soup = BeautifulSoup(html_content.text, "lxml")

    title_text = soup.find(id="content").find("h1").text
    comments_text = soup.find("div", id="content").find_all("div", class_="texts")

    parse_page = {
        "title": title_text.split("\xa0 :: \xa0")[0].strip(),
        "author": title_text.split("\xa0 :: \xa0")[1].strip(),
        "link_img": soup.find("div", class_="bookimage").find("img")["src"],
        "comments": [comment.find("span", class_="black").text for comment in comments_text],
        "genres": [genre.text for genre in soup.find("div", id="content").find("span", class_="d_book").find_all("a")],
    }

    return parse_page


def download_txt(url: str, book_id: int, filename: str, folder: str = "books/") -> Optional[str]:
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        book_id: Номер книги
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(f"{url}txt.php", params={"id": book_id})
    response.raise_for_status()

    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)

    path_filename = os.path.join(folder, f"{sanitize_filename(filename)}.txt")

    with open(path_filename, "w", encoding="utf-8") as file:
        file.write(response.text)
    return path_filename


def download_img(url: str, folder: str = "images/") -> Optional[str]:
    """Функция для скачивания картинок файлов.
    Args:
        url (str): Cсылка на картинку, которую хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()

    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = urlsplit(url, scheme='', allow_fragments=True).path.split("/")[-1]

    path_filename = os.path.join(folder, filename)

    with open(path_filename, "wb") as file:
        file.write(response.content)
    return path_filename



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

    books_description = []

    for page in range(1, 5):
        link_category_page = urljoin(link_category, str(page))

        try:
            response = requests.get(link_category_page)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            sys.stderr.write(f"Ошибка соединения\n")
            logger.error(f"Ошибка соединения")
            time.sleep(3)
            continue
        except requests.exceptions.HTTPError:
            sys.stderr.write(f"Ошибка на странице\n")
            logger.error(f"Ошибка на странице")
            continue

        soup = BeautifulSoup(response.text, "lxml")
        parse_content_table = soup.find(id="content").find_all("table")

        for book in parse_content_table:
            book_href = book.find("a")["href"]
            book_link = urljoin(url, book_href)
            book_id = book_href[2:-1]

            try:
                book_link_response = requests.get(book_link)
                book_link_response.raise_for_status()
                check_for_redirect(book_link_response)
            except requests.exceptions.ConnectionError:
                sys.stderr.write(f"Ошибка соединения на {book_link}\n")
                logger.error(f"Ошибка соединения на {book_link}")
                time.sleep(3)
                continue
            except requests.exceptions.HTTPError:
                sys.stderr.write(f"Ошибка на странице {book_link}\n")
                logger.error(f"Ошибка на странице {book_link}")
                continue

            book_parse = parse_book_page(book_link_response)
            book_filename = f"{book_id}. {book_parse['title']}"

            try:
                download_txt(url, book_id, book_filename)
                download_img(urljoin(book_link, book_parse["link_img"]))
            except requests.exceptions.ConnectionError:
                sys.stderr.write(f"Ошибка соединения при скачивании {book_id} книги\n")
                logger.error(f"Ошибка соединения при скачивании {book_id} книги")
                time.sleep(3)
                continue
            except requests.exceptions.HTTPError:
                sys.stderr.write(f"Ошибка на странице при скачивании {book_id} книги\n")
                logger.error(f"Ошибка на странице при скачивании {book_id} книги")
                continue

            books_description.append(book_parse)

        logger.info(f"Парсер успешно распарсил страницу {page}")

    with open("books_description.json", "w", encoding="utf-8") as json_file:
        json.dump(books_description, json_file, indent=2, ensure_ascii=False)

    logger.info("Парсер успешно завершил работу")
    print("Парсер успешно завершил работу")


if __name__ == "__main__":
    main()
