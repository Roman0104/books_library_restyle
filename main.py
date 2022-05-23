import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()


def download_txt(url: str, filename: str, folder: str = "books/") -> Optional[str]:
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

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


def main(url: str) -> None:

    for index in range(1, 11):
        url_page = f"{url}/b{index}/"
        response = requests.get(url_page)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        soup = BeautifulSoup(response.text, "lxml")

        title_text = soup.find(id="content").find("h1").text

        title = title_text.split("\xa0 :: \xa0")[0].strip()

        link_img = soup.find("div", class_="bookimage").find("img")["src"]
        url_img = urljoin(url, link_img)

        url_txt = f"{url}txt.php?id={index}"
        filename_text = f"{index}. {title}"

        # download_txt(url_txt, filename_text)
        # download_img(url_img)

        comments_text = soup.find("div", id="content").find_all("div", class_="texts")
        print(title)
        for comment in comments_text:
            print(comment.find("span", class_="black").text)
        print()


if __name__ == "__main__":

    url = "https://tululu.org/"

    main(url)
