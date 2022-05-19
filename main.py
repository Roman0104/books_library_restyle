import requests
from pathlib import Path


def main() -> None:
    url = "https://tululu.org/txt.php?id="

    for index in range(1, 11):
        response = requests.get(url+str(index))
        response.raise_for_status()
        print(f"requests - {index}")

        with open(f"books/id{index}.txt", "w", encoding="utf-8") as file:
            file.write(response.text)


if __name__ == "__main__":
    Path("books").mkdir(parents=True, exist_ok=True)

    main()
