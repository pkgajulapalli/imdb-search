import imdb
import sys

ia = imdb.IMDb()


def run():
    movies = ia.search_movie('matrix')
    print(movies[0])


def search_movies(actor_name):
    actor = search_person(actor_name)
    result = ia.get_person_filmography(actor.personID)
    movies: imdb.Movie.Movie = result['data']['filmography'][0]['actor']
    movie_list = []
    for m in movies:
        movie = ia.get_movie(m.getID())
        new_entry = {'title': movie.get('title'), 'year': movie.get('year'), 'rating': movie.get('rating')}
        if new_entry['rating'] is None:
            new_entry['rating'] = 0.0
        if new_entry['year'] is None:
            new_entry['year'] = 0
        movie_list.append(new_entry)
        if len(movie_list) % 10 == 0:
            print('Processed %d movies' % (len(movie_list)))

    print('Got %d movies of %s' % (len(movie_list), actor_name))
    sorted_movie_list = sorted(movie_list, key=lambda m: (m['rating'], m['year']), reverse=True)
    for movie in sorted_movie_list:
        print('Movie: %s (%d) (%d)' % (movie['title'], movie['rating'], movie['year']))


def search_person(name):
    people = ia.search_person(name=name)
    print('Number of people with name \'%s\': %d' % (name, len(people)))
    return people[0]


if __name__ == '__main__':
    actor_name = sys.argv[1]
    print('Searching for movies \'%s\' acted in...' % (actor_name))
    search_movies(actor_name)
