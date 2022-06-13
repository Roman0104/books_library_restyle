import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def main():

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


def on_reload():
    with open("books_description.json", "r", encoding="utf-8") as json_file:
        books_description = json.loads(json_file.read())

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')

    rendered_page = template.render(
        books_description=books_description,
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == "__main__":
    main()
