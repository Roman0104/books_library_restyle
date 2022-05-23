import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
from pathvalidate import sanitize_filename


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

    path_filename = f"{folder}{sanitize_filename(filename)}.txt"

    with open(path_filename, "w", encoding="utf-8") as file:
        file.write(response.text)
    return path_filename


def main(url: str) -> None:

    for index in range(1, 11):
        url_page = url + "/b" + str(index) + "/"
        response = requests.get(url_page)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        soup = BeautifulSoup(response.text, "lxml")

        title_text = soup.find(id="content").find("h1").text

        title = title_text.split("\xa0 :: \xa0")[0].strip()

        url_txt = url + "txt.php?id=" + str(index)
        filename = f"{index}. {title}"

        download_txt(url_txt, filename)


if __name__ == "__main__":

    url = "https://tululu.org/"

    main(url)
