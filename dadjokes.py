import tornado.web
import tornado.ioloop
import requests
import logging

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        joke = get_random_joke()

        # output to console
        print(joke)

        # output to webpage
        self.write(joke)


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


def get_random_joke():
    headers = {'user-agent': 'ewehner', 'Accept': 'text/plain'}
    r = requests.get("https://icanhazdadjoke.com/", headers=headers)
    return r.text



if __name__ == "__main__":
    static_url_prefix = "/static/"
    dad_jokes = tornado.web.Application([
        (r"/", MainHandler),
        (r"/markov.*", BuildAJokeHandler)
    ], debug=True)

    logging.warning('DadJokes is now listening on port 8888...')
    dad_jokes.listen(8888)
    tornado.ioloop.IOLoop.current().start()