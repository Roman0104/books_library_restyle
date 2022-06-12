import argparse
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


def parse_book_page(html_content) -> dict:

    soup = BeautifulSoup(html_content.text, "lxml").select_one(".ow_px_td")

    title_text = soup.select_one("h1").text
    comments_text = soup.select("div .texts")

    parse_page = {
        "title": title_text.split("\xa0 :: \xa0")[0].strip(),
        "author": title_text.split("\xa0 :: \xa0")[1].strip(),
        "link_img": soup.select_one(".bookimage img")["src"],
        "comments": [comment.select_one("span.black").text for comment in comments_text],
        "genres": [genre.text for genre in soup.select("span.d_book a")],
    }

    return parse_page


def main() -> None:
    logger = logging.getLogger("books_parser")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("main.log",
                                       mode='w',
                                       encoding='utf-8', )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    parser = argparse.ArgumentParser(
        description="Программа парсинга книг с сайта tululu.org"
    )
    parser.add_argument("-s",
                        "--start_id",
                        type=int,
                        default=1,
                        help="С какой страницы начать парсинг",
                        )
    parser.add_argument("-e",
                        "--end_id",
                        type=int,
                        default=11,
                        help="На какой страницы закончить парсинг",
                        )
    args = parser.parse_args()
    logger.info(f"start_id = {args.start_id}, end_id = {args.end_id}")

    url = "https://tululu.org/"

    for index in range(args.start_id, args.end_id):
        link_page = f"{url}/b{index}/"
        try:
            response = requests.get(link_page)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.ConnectionError:
            sys.stderr.write(f"Ошибка соединения на {index} книге\n")
            logger.error(f"Ошибка соединения на {index} книге")
            time.sleep(3)
            continue
        except requests.exceptions.HTTPError:
            sys.stderr.write(f"Ошибка на странице {index} книги\n")
            logger.error(f"Ошибка на странице {index} книги")
            continue

        book_parse = parse_book_page(response)
        book_filename = f"{index}. {book_parse['title']}"

        try:
            download_txt(url, index, book_filename)
            download_img(urljoin(link_page, book_parse["link_img"]))
        except requests.exceptions.ConnectionError:
            sys.stderr.write(f"Ошибка соединения при скачивании {index} книги\n")
            logger.error(f"Ошибка соединения при скачивании {index} книги")
            time.sleep(3)
            continue
        except requests.exceptions.HTTPError:
            sys.stderr.write(f"Ошибка на странице при скачивании {index} книги\n")
            logger.error(f"Ошибка на странице при скачивании {index} книги")
            continue

        logger.info(f"Парсер успешно скачал книгу {index}")


if __name__ == "__main__":
    main()
