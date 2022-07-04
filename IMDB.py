import grequests
import requests
from bs4 import BeautifulSoup
import conf
import time
import logging

logging.basicConfig(filename='movies.log')
logging.basicConfig(level=logging.INFO)


def get_urls(url):
    """

    @param url:
    @return:
    """
    r = requests.get(url)
    if r:
        print(True)
        logger.info('The request has succeeded')
    else:
        logging.warning('The request was not successful')
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    scraped_movies = soup.find_all('td', {'class': 'titleColumn'})
    urls = (conf.WEBSITE + movie.find('a')['href'] for movie in scraped_movies)
    return urls


def get_data_requests(urls):
    resp = (requests.get(url) for url in urls)
    return resp


def get_data_grequests(urls):
    """

    @param urls:
    @return:
    """
    reqs = (grequests.get(link) for link in urls)
    resp = grequests.map(reqs, size=conf.NO_BATCHES)
    return resp


def print_data(resp):
    """

    @param resp:
    @return:
    """
    for i, r in enumerate(resp, 1):
        # hacer log aca
        soup = BeautifulSoup(r.text, 'html.parser')
        movie = soup.find('h1').get_text()

        links = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
        directors = set()
        for link in links:
            if 'tt_ov_dr' in str(link):
                director = link.text
                directors.add(director)
        directors = ', '.join(directors)
        print(f'{i} - {movie} - {directors}')
    return


def main():
    """

    """
    start = time.perf_counter()
    urls = get_urls(conf.IMDB_250_URL)
    resp = get_data_requests(urls)
    print_data(resp)
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    urls = get_urls(conf.IMDB_250_URL)
    resp = get_data_grequests(urls)
    print_data(resp)
    end = time.perf_counter()
    print(end - start)

    TIME_TAKEN = 129.699939045


if __name__ == '__main__':
    main()
