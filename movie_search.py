import os
from imdb import Cinemagoer
from itertools import groupby
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import logging.config

ia = Cinemagoer()
short_movie_genre = 'Short'


def get_movie_details(movie_id, contribution_type):
    movie = ia.get_movie(movie_id)
    short_movie_kind_prefix = ''
    try:
        short_movie_kind_prefix = 'Short ' if short_movie_genre in movie['genres'] else ''
    except:
        pass

    movie_details = {'title': movie.get('title'),
                     'year': movie.get('year'),
                     'kind': short_movie_kind_prefix + movie.get('kind'),
                     'contribution_type': contribution_type,
                     'rating': movie.get('rating')}
    if movie_details['rating'] is None:
        movie_details['rating'] = 0.0
    if movie_details['year'] is None:
        movie_details['year'] = 0
    if movie_details['kind'] is None:
        movie_details['kind'] = 'NA'
    return movie_details


def get_movies(filmography):
    movie_list = []
    for contribution_type in filmography.keys():
        for movie in filmography[contribution_type]:
            movie_list.append((movie.getID(), contribution_type))
    movie_list.sort(key=lambda m: m[0])
    return [(key, ', '.join(j for i, j in group)) for key, group in groupby(movie_list, key=lambda x: x[0])]


def search_movies(name):
    person = search_person(name)
    logging.info('Name: %s' % person.__str__())
    logging.info('Image: %s' % person.get_fullsizeURL())

    result = ia.get_person_filmography(person.personID)
    movies = get_movies(result['data']['filmography'])
    movie_list = []

    print('Getting results of %d projects' % len(movies))
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_movie_details, movie[0], movie[1]) for movie in movies}

        for future in as_completed(futures):
            try:
                movie_list.append(future.result())
            except Exception as exc:
                logging.error('Could not process request due to: %s' % exc)

    logging.info('Got %d movies of %s' % (len(movie_list), name))
    sorted_movie_list = sorted(movie_list, key=lambda m: (m['kind'], m['rating'], m['year']), reverse=True)
    for movie in sorted_movie_list:
        logging.info('%s (%.1f) (%d) (%s) (%s)' % (
            movie['title'], movie['rating'], movie['year'], movie['kind'], movie['contribution_type']))


def search_person(name):
    people = ia.search_person(name=name)
    logging.info('Number of people with name \'%s\': %d' % (name, len(people)))
    if len(people) == 0:
        logging.info('Couldn\'t find %s in imdb. Please check the spelling.' % name)
        sys.exit()
    return people[0]


if __name__ == '__main__':
    logging.config.fileConfig(os.path.dirname(os.path.realpath(__file__)) + '/logging.conf')
    person_name = sys.argv[1]
    logging.info('Searching for movies \'%s\' has been part of...' % person_name)
    search_movies(person_name)
