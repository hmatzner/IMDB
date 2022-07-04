import grequests
import requests
from bs4 import BeautifulSoup
import conf
import time
import logging
import sys

logger = logging.getLogger('IMDB')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

file_handler = logging.FileHandler('movies.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.ERROR)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_urls(url):
    """
    Performs a request and parses the data of the website to scrape
    @param url: main link of the website to scrape
    @return: urls, which are the links of every movie
    """
    r = requests.get(url)
    if r:
        logger.info('The request has succeeded')
    else:
        logger.error('The request was not successful')
    html = r.text
    soup = BeautifulSoup(html, 'html.parser')
    scraped_movies = soup.find_all('td', {'class': 'titleColumn'})
    urls = (conf.WEBSITE + movie.find('a')['href'] for movie in scraped_movies)
    return urls


def get_data_requests(urls):
    """
    Makes a request with the module requests for each url and gets all the responses
    @param urls: all the urls of the movies
    @return: resp, which are the responses received
    """
    resp = (requests.get(url) for url in urls)
    return resp


def get_data_grequests(urls):
    """
    Makes a request with the module grequests for each url and gets all the responses
    @param urls: all the urls of the movies
    @return: resp, which are the responses received
    """
    reqs = (grequests.get(link) for link in urls)
    resp = grequests.map(reqs, size=conf.NO_BATCHES)
    return resp


def print_data(resp):
    """
    Parses the data for each response and prints the ranking, name and director for each movie.
    @param resp: responses of the requests provided by the get_data function
    """
    for i, r in enumerate(resp, 1):
        soup = BeautifulSoup(r.text, 'html.parser')
        movie = soup.find('h1').get_text()

        if r:
            logger.info(f"The request for movie {i}. '{movie}' was successful")
        else:
            logger.error(f"The request for movie {i}. '{movie}' was not successful")

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
    Main function of the module:
    - calls the rest of the functions and times them, first with the
    requests module and then with the grequests module.
    """
    print('Performing the web scraping task with the requests module...')
    start = time.perf_counter()
    urls = get_urls(conf.IMDB_250_URL)
    resp = get_data_requests(urls)
    print_data(resp)
    end = time.perf_counter()
    print(f'Time taken to get the data with requests module: {end - start} seconds.\n')

    print('Performing the web scraping task with the grequests module...')
    start = time.perf_counter()
    urls = get_urls(conf.IMDB_250_URL)
    resp = get_data_grequests(urls)
    print_data(resp)
    end = time.perf_counter()
    print(f'Time taken to get the data with grequests module: {end - start} seconds.')


if __name__ == '__main__':
    main()
