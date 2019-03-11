import tornado.web
import tornado.ioloop
import requests
import logging
import re


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        joke = self.get_random_joke()

        # output to console
        print(joke)

        # output to webpage
        self.write(joke)

    def get_random_joke(self):
        headers = {'user-agent': 'ewehner', 'Accept': 'text/plain'}
        r = requests.get("https://icanhazdadjoke.com/", headers=headers)
        return r.text

class BuildAJokeHandler(tornado.web.RequestHandler):
    def get(self):
        new_joke = ''
        step = 0

        while (True):

            joke = get_random_joke().lower()
            joke_words = joke.split()
            print(joke_words)

            if step < len(joke_words):
                new_joke += joke_words[step] + ' '
                step += 1
            else:
                break

        print(new_joke)
        self.write(new_joke)

class ListHandler(tornado.web.RequestHandler):
    def get(self):
        jokes = self.get_page_of_jokes()
        self.render('list.html', title="Woo Dad Jokes!", items=jokes)

    def get_page_of_jokes(limit=30, page=1):
        headers = {'user-agent': 'ewehner', 'Accept': 'application/json'}
        payload = {"limit": limit, "page": page}

        r = requests.get("https://icanhazdadjoke.com/search",
                         headers=headers,
                         params=payload)
        jokes = r.json()['results']
        lotsa_jokes = list(map(lambda x: x['joke'], jokes))

        return lotsa_jokes


class JokeMakerHandler(tornado.web.RequestHandler):
    def get(self):
        jokes = self.get_list_of_jokes()

        self.find_markov_choices(jokes)
        # self.render('list.html', title="All the Dad Jokes!", items=jokes)

    def find_markov_choices(self, joke_list):

        # split jokes into individual words
        words = []
        for joke in joke_list:
            words += joke.split()

        # get all the end of sentence words
        end_words = []
        for word in words:
            if word[-1] in ['.', '!', '?'] and word != '.':
                end_words.append(word)

        trimmed_words = []
        for word in words:
            trimmed_words.append(re.sub(r'[^\w\s]', '', word))

        # create a dict with unique keys mapped to a list of choices
        word_map = dict.fromkeys(trimmed_words, [])
        print(word_map.items())

        for key, choices in word_map.items():
            locations = [i for i, j in enumerate(trimmed_words) if j == key]
            # print("key: ", key, "  locations: ", locations)
            for i in locations:
                if i + 1 < len(trimmed_words):
                    word_map[key].append(trimmed_words[i+1])
            # print("word: ", key, " choices: ", word_map[key])


        # smoosh all the joke words together: DONE
    #     then separate them into a big list of words DONE
    #       then for each word find all instances. Then choose the following word for each, and store them associated with that word. stash them in redis.

    def get_list_of_jokes(self):

        headers = {'user-agent': 'ewehner', 'Accept': 'application/json'}
        payload = {"limit": "30", "page": 1}
        r = requests.get("https://icanhazdadjoke.com/search",
                     headers=headers,
                     params=payload)
        total_num_jokes = r.json()['total_jokes']
        print("total number of jokes = ", total_num_jokes)

        results = r.json()['results']

        page = 2

        while (len(results) < total_num_jokes):

            payload = {"limit": "30", "page": page}
            r = requests.get("https://icanhazdadjoke.com/search",
                             headers=headers,
                             params=payload)
            results += (r.json()['results'])

            page += 1

        jokes = list(each['joke'] for each in results)

        return jokes


if __name__ == "__main__":
    static_url_prefix = "/static/"
    dad_jokes = tornado.web.Application([
        (r"/", JokeMakerHandler),
        (r"/markov.*", JokeMakerHandler),
        (r"/list.*", ListHandler)
    ], debug=True)

    logging.warning('DadJokes is now listening on port 8888...')
    dad_jokes.listen(8888)
    tornado.ioloop.IOLoop.current().start()
