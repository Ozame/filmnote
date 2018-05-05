import requests
from bs4 import BeautifulSoup
import configparser
import re 
import time

config = configparser.ConfigParser()
config.read('config.ini')
API_KEY = config['Default']['API_KEY']
REGEX_YEAR = re.compile(r"\d{4}")
REGEX_INFO = re.compile(r"\(.*?\)")


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
        self.keyword = ""

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
        description = 
            box.find('p', class_="moviepromo__description").find('span').string
        
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
        film.year = parse_year(description)
        film.keyword = parse_keyword(description)
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


def parse_year(description):
    """Parses the movie year from the description. If not found, 
    returns empty string."""
   
    years = REGEX_YEAR.findall(description)
    if years:
        return years[0]
    else:
        return ""


def parse_keyword(description):
    """Tries to parse part of the movie title in the description's parenthesis 
    section

    The original title is usually in the description's beginning in parenthesis, 
    but this is not a standard, so this might be useless
    """

    info = REGEX_INFO.findall(description)
    key = ""
    if not info:
        return ""
    info = info[0][1:-1]

    if info is 'U':
        return ""

    # TODO: Some titles have - before the finnish title, check for it?
    try:
        ind_slash = info.index('/')
    except ValueError:
        ind_slash = 500
    try:
        ind_comma = info.index(',')
    except ValueError:
        ind_comma = 500

    if ind_slash < ind_comma:
        key = info[:ind_slash]
    elif ind_comma < ind_slash:
        key = info[:ind_comma]
    else:
        key = info

    m = REGEX_YEAR.search(key)
    if m:
        key = key[:m.start()]
    return key.strip()



def create_request(movie, useKeyword=False):
    """Creates the api request with given movies title and year"""

    # plot = 'short'
    if useKeyword:
        name = movie.keyword.replace(' ', '+') 
    else:
        name = movie.name.replace(' ', '+')
    call = ("http://www.omdbapi.com/?apikey=" + API_KEY + "&t=" + name
            +  '&y=' + movie.year)
    return call


def request_data(movie, useKeyword=False):
    """Requests the data from the api"""

    call = create_request(movie, useKeyword)
    try:
        response = requests.get(call, timeout=0.1)
        data = response.json()
        return data
    except requests.exceptions.Timeout:
        return {"Response":"False","Error":"Movie not found!"}
    
def update_movies(movies):
    """ Updates info for the movies
    
    Returns dict, {'updated':[], 'failed':[]}, where 'updated' contains 
    succesfully updated movies, and 'failed' contains movies that 
    couldn't be updated
    """

    movie_dict = {'updated':[], 'failed':[]}
    for movie in movies:
        time.sleep(0.2)
        succesful_fetch = fetch_info(movie)
        if succesful_fetch:
            movie_dict['updated'].append(movie)
        else:
            movie_dict['failed'].append(movie)  

    return movie_dict

def fetch_info(movie):
    """ Fetches given movie's info from OMDb api"""
    
    data = request_data(movie, False)
    if (data['Response'] == 'True'):
        set_info(movie, data)
    else:
        data = request_data(movie, True)
        if (data['Response'] == 'True'):
            set_info(movie, data)
        else:
            return False
    return True
   


def main():
    x = "http://www.telkku.com/elokuvat"
    data = fetch_data(x)
    #t = parse_keyword("(Police Academy 1984). Klassikkokomedia tarjoaa vauh")
    #print(t)
    update_movies(data)


if __name__ == "__main__":
    main()
