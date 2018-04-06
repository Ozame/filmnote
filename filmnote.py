import requests
from bs4 import BeautifulSoup
import configparser 

config = configparser.ConfigParser()
config.read('config.ini')
API_KEY = config['Default']['API_KEY']


class Film():

    def __init__(self, name, year="", genres=[],
                 director="", actors=[], ratings=[]):
        self.name = name
        self.year = year
        self.genres = genres
        self.director = director
        self.actors = actors
        self.plot = ""
        self.ratings = ratings
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
        name = clean_name(box.find('h1', class_="moviepromo__title").string)
        film = Film(name)
        film.photo_url = purl
        film.channel = channel
        film.time = time
        movies.append(film)
    return movies

def clean_name(raw):
    """ Clean up the age limits, channel-related stuff etc from the given 
        name, return the cleaned one
    """
    new = raw

    # age limits
    if '(' in new:
        p_ind = new.find('(')
        new = raw[:p_ind]

    # channel stuff and movie series
    prefixes =  ["kino", "leffa", "klassik"]
    if ':' in new:
        c_ind = new.find(':')
        for pf in prefixes:
            if pf in new[:c_ind].lower():
                new = new[c_ind + 1:]
                break 
    return new.strip()



def update_movies(movies):
    """ Updates info for the movies"""

    for movie in movies:
        update_info(movie)

def update_info(movie):
    """ Fetches given movies info from OMDb api"""
    plot = 'short'
    name = movie.name.replace(' ', '+')

    call = ("http://www.omdbapi.com/?apikey=" + API_KEY + "&t=" + name) 
    # TODO: Year to search and handle the not working titles
    # +  '&y=' + movie.year)
    print(call)
    #response = requests.get(call)
    #data = response.json()
    #print(data['Response'])
    #print(data)








def main():
    # a = "http://www.leffatykki.com/telkku/seuraava"
    # b = "http://wwww.kake.fi"
    # c = "http://www.telkku.com/tv-ohjelmat/2018-04-01/peruskanavat/koko-paiva/"
    x = "http://www.telkku.com/elokuvat"
    data = fetch_data(x)
    update_movies(data)


if __name__ == "__main__":
    main()
