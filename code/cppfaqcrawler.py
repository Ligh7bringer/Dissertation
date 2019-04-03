import requests
from ruamel.yaml import YAML
from bs4 import BeautifulSoup as bs4
import os
import threading

data = []
DATA_DIR = os.path.join(os.getcwd(), 'data')
FILE_EXT = '.yaml'


def write_to_file():
    formatted_data = dict(categories=['faq', 'cpp'], conversations=data)

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    yaml = YAML()
    yaml.default_flow_style = False

    out_file = os.path.join(DATA_DIR, str(threading.get_ident()) + FILE_EXT)

    with open(out_file, 'w+', encoding="utf-8") as outfile:
        yaml.dump(formatted_data, outfile)


def crawl_pages(url):
    page_src = requests.get(url).text
    soup = bs4(page_src, 'lxml')

    for a in soup.findAll('a'):
        href = a['href']
        if href.startswith('/wiki'):
            a['href'] = a['href'].replace(href, 'https://isocpp.org' + href)

    result = soup.find_all(['h3', 'p', 'pre', 'ul', 'ol', 'li', 'code'])

    question = None
    answer = []
    found_question = False

    for r in result:

        if found_question and question is not None:
            str_r = str(r)

            if str_r.startswith('<p') or str_r.startswith('<pre') or str_r.startswith('<ul') or str_r.startswith('<ol'):
                answer.append(str(r))

            elif str(r).startswith('<h3'):
                j_answer = ' '.join(answer)
                entry = [question, j_answer]
                data.append(entry)
                answer.clear()
                found_question = False
                question = None

        if str(r).startswith('<h3'):
            found_question = True
            question = str(r.text)

    write_to_file()


if __name__ == "__main__":
    urls = ['https://isocpp.org/wiki/faq/big-picture', 'https://isocpp.org/wiki/faq/newbie', ]
    for url in urls:
        crawl_pages(url)
