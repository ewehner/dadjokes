import tornado.web
import tornado.ioloop
import requests
import logging
import re
import random
import redis
import json


class RealJokeHandler(tornado.web.RequestHandler):
    # Returns a random, actual Dad joke
    def get(self):
        joke = self.get_random_joke()

        # output to webpage
        self.write(joke)

    def get_random_joke(self):
        headers = {'user-agent': 'ewehner', 'Accept': 'text/plain'}
        r = requests.get("https://icanhazdadjoke.com/", headers=headers)
        return r.text


class ListHandler(tornado.web.RequestHandler):
    # Returns a list of all (real) Dad jokes
    def get(self):
        r = redis.Redis(host='localhost', port=6379)
        r.flushall()

        if r.exists('joke_list'):
            joke_list = json.loads(r.get('joke_list'))
        else:
            joke_list = get_list_of_jokes()
            r.set('joke_list', json.dumps('joke_list'))

        self.render('list.html', title="Woo Dad Jokes!", items=joke_list)


class JokeMakerHandler(tornado.web.RequestHandler):
    # Creates a markov-generated Dad joke
    def get(self):
        r = redis.Redis(host='localhost', port=6379)

        # If a markov map exists in the cache, snag data from redis
        if r.exists('markov_map'):
            self.markov_map = json.loads(r.get('markov_map'))
            self.start_words = json.loads(r.get('start_words'))
            self.end_words = json.loads(r.get('end_words'))

        # if it doesn't, build the markov map and other data, and stash it in redis for later
        else:
            self.jokes = get_list_of_jokes()
            r.set('joke_list', json.dumps(self.jokes))

            self.start_words, self.end_words = self.get_beginning_and_end_words(self.jokes)
            r.set('start_words', json.dumps(self.start_words))
            r.set('end_words', json.dumps(self.end_words))

            self.markov_map = self.find_markov_choices(self.jokes)
            r.set('markov_map', json.dumps(self.markov_map))

        new_joke = self.build_joke(self.markov_map)

        self.render('joke.html', title="All the Dad Jokes!", joke=new_joke)


    def find_markov_choices(self, joke_list):

        # split jokes into individual words
        words = []
        for joke in joke_list:
            words += joke.split()

        # get all the end of sentence words
        index = 0
        trimmed_words = []

        for word in words:
            if word[-1] in ['.', '!', '?']:
                # blerp marks the end of a joke
                words.insert(index + 1, 'blerp')
            index += 1
            trimmed_words.append(re.sub(r'[^\w\s]', '', word))
            print(trimmed_words)

        #
        # for word in words:
        #     trimmed_words.append(re.sub(r'[^\w\s]', '', word))

        # create a dict with unique keys mapped to a list of choices
        word_map = dict.fromkeys(trimmed_words, [])

        for key, choices in word_map.items():
            locations = [i for i, j in enumerate(trimmed_words) if j == key]
            temp = []
            for i in locations:
                # map word choices except end words --> words that start the next joke
                if i + 1 < len(trimmed_words) and trimmed_words[i + 1] != 'blerp':
                    temp.append(trimmed_words[i + 1])
            word_map[key] = temp

        return word_map

    def build_joke(self, markov_map):

        new_joke = ''
        current_word = random.choice(self.start_words)
        new_joke += current_word + ' '

        # Add words until you hit an end word (one with no associated choices)
        while True:
            choices = list(markov_map[current_word])
            if not choices:
                break
            next_word = random.choice(choices)
            current_word = next_word
            new_joke += next_word + ' '

        return new_joke


    def get_beginning_and_end_words(self, jokes):
        beginnings = []
        endings = []

        for joke in jokes:
            words = joke.split()
            beginnings.append(words[0])
            endings.append(words[-1])

        return beginnings, endings

def get_list_of_jokes():
    # Gets a list of all the jokes -- used by both handler classes above
    headers = {'user-agent': 'ewehner', 'Accept': 'application/json'}
    payload = {"limit": "30", "page": 1}
    resp = requests.get("https://icanhazdadjoke.com/search",
                     headers=headers,
                     params=payload)
    total_num_jokes = resp.json()['total_jokes']

    results = resp.json()['results']

    page = 2

    while (len(results) < total_num_jokes):
        payload = {"limit": "30", "page": page}
        resp = requests.get("https://icanhazdadjoke.com/search",
                         headers=headers,
                         params=payload)
        results += (resp.json()['results'])

        page += 1

        joke_list = list(each['joke'] for each in results)

        return joke_list


if __name__ == "__main__":
    static_url_prefix = "/static/"

    dad_jokes = tornado.web.Application([
        (r"/", JokeMakerHandler),
        (r"/list.*", ListHandler),
        (r"/real.*", RealJokeHandler)
    ], debug=True)

    logging.warning('DadJokes is now listening on port 8888...')
    dad_jokes.listen(8888)
    tornado.ioloop.IOLoop.current().start()
