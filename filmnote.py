import requests
from bs4 import BeautifulSoup


class Film():

    def __init__(self, name, year=None, genres=None,
                 director=None, actors=None, rating=None):
        self.name = name
        self.year = year
        self.genres = genres
        self.director = director
        self.actors = actors
        self.rating = rating
        self.photo_url = ""
        self.channel = ""
        self.time = ""

    def __str__(self):
        return "{} ({})".format(self.name, self.year)


def fetch_data(url):
    """Fetches new movie data from the url"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    movieboxes = soup.find_all('article', class_="moviepromo")
    movies = []
    for box in movieboxes:
        purl = box.find('img')['src']
        channel = box.find('dt',
                           class_="moviepromo__channel").find('img')['alt']
        timespans = box.find('dd', class_="moviepromo__time").find_all('span')
        time_list = []
        for span in timespans:
            time_list.append(span.string)
        time = ''.join(time_list)
        name = box.find('h1', class_="moviepromo__title").string
        film = Film(name)
        film.photo_url = purl
        film.channel = channel
        film.time = time
        movies.append(film)


def update_movies(movies):
    """ Updates info for the movies"""

    for movie in movies:
        update_info(movie)


def update_info(movie):
    """ Fetches given movies info from TheMovieDb"""

def main():
    # a = "http://www.leffatykki.com/telkku/seuraava"
    # b = "http://wwww.kake.fi"
    # c = "http://www.telkku.com/tv-ohjelmat/2018-04-01/peruskanavat/koko-paiva/"
    x = "http://www.telkku.com/elokuvat"
    data = fetch_data(x)
    update_info(data)


if __name__ == "__main__":
    main()
