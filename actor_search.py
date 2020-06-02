import imdb
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import logging.config

ia = imdb.IMDb()


def get_movie_details(movie_id):
    movie = ia.get_movie(movie_id)
    movie_details = {'title': movie.get('title'), 'year': movie.get('year'), 'rating': movie.get('rating')}
    if movie_details['rating'] is None:
        movie_details['rating'] = 0.0
    if movie_details['year'] is None:
        movie_details['year'] = 0
    return movie_details


def search_movies(person_name):
    actor = search_person(person_name)
    result = ia.get_person_filmography(actor.personID)
    movies: imdb.Movie.Movie = result['data']['filmography'][0]['actor']
    movie_list = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_movie_details, movie.getID()) for movie in movies}

        for future in as_completed(futures):
            try:
                movie_list.append(future.result())
            except Exception as exc:
                logging.error('Could not process request due to: %s' % exc)

    logging.info('Got %d movies of %s' % (len(movie_list), person_name))
    sorted_movie_list = sorted(movie_list, key=lambda m: (m['rating'], m['year']), reverse=True)
    for movie in sorted_movie_list:
        logging.info('Movie: %s (%d) (%d)' % (movie['title'], movie['rating'], movie['year']))


def search_person(name):
    people = ia.search_person(name=name)
    logging.info('Number of people with name \'%s\': %d' % (name, len(people)))
    return people[0]


if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')
    actor_name = sys.argv[1]
    logging.info('Searching for movies \'%s\' acted in...' % actor_name)
    search_movies(actor_name)
