import argparse
import json
import logging
import sys
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from main import check_for_redirect, parse_book_page, download_txt, download_img


def main() -> None:
    logger = logging.getLogger("parse_tululu_category")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("parse_tululu_category.log",
                                       mode='w',
                                       encoding='utf-8', )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    parser = argparse.ArgumentParser(
        description="Программа парсинга книг с сайта tululu.org по категориям"
    )
    parser.add_argument("-s",
                        "--start_page",
                        type=int,
                        default=1,
                        help="С какой страницы начать скачивать книги",
                        )
    parser.add_argument("-e",
                        "--end_page",
                        type=int,
                        default=701,
                        help="По какую страницу скачивать книги",
                        )
    parser.add_argument("-f",
                        "--dest_folder",
                        default="",
                        help="Путь к каталогу с результатами парсинга: картинкам, книгам, JSON",
                        )
    parser.add_argument("-i",
                        "--skip_imgs",
                        action='store_true',
                        help="Не скачивать картинки",
                        )
    parser.add_argument("-t",
                        "--skip_txt",
                        action='store_true',
                        help="Не скачивать книги",
                        )
    parser.add_argument("-j",
                        "--json_path",
                        default="books_description",
                        help="Путь к *.json файлу с результатами",
                        )
    args = parser.parse_args()
    dest_folder = f"{args.dest_folder}/" if args.dest_folder else ""
    json_path = args.json_path
    logger.info(f"start_page={args.start_page}, "
                f"end_page={args.end_page}, "
                f"dest_folder={args.dest_folder}, "
                f"skip_imgs={args.skip_imgs}, "
                f"skip_txt={args.skip_txt}"
                )

    url = "https://tululu.org/"
    book_category = "/l55/"
    link_category = urljoin(url, book_category)

    books_description = []

    for page in range(args.start_page, args.end_page + 1):
        link_category_page = urljoin(link_category, str(page))

        try:
            response = requests.get(link_category_page)
            response.raise_for_status()
            check_for_redirect(response)
        except requests.exceptions.ConnectionError:
            sys.stderr.write(f"Ошибка соединения\n")
            logger.error(f"Ошибка соединения")
            time.sleep(3)
            continue
        except requests.exceptions.HTTPError:
            sys.stderr.write(f"Ошибка на странице {link_category_page}\n")
            logger.error(f"Ошибка на странице {link_category_page}")
            continue

        soup = BeautifulSoup(response.text, "lxml").select(".ow_px_td .d_book")

        book_ids = [id.select_one("a")["href"][2:-1] for id in soup]

        for book_id in book_ids:
            book_link = urljoin(url, f"/b{book_id}/")
            print(book_link)

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
                if not args.skip_txt:
                    download_txt(
                        url,
                        book_id,
                        book_filename,
                        f"{dest_folder}books/"
                    )
                if not args.skip_imgs:
                    download_img(
                        urljoin(book_link, book_parse["link_img"]),
                        f"{dest_folder}images/"
                    )
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

    json_path = f"{dest_folder}{json_path}.json"
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(books_description, json_file, indent=2, ensure_ascii=False)

    logger.info("Парсер успешно завершил работу")
    print("Парсер успешно завершил работу")


if __name__ == "__main__":
    main()
