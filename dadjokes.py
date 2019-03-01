import tornado.web
import tornado.ioloop
import requests
import logging

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        joke = get_random_joke()

        # output to console
        print(joke.text)

        # output to webpage
        self.write(joke.text)


class BuildAJokeHandler(tornado.web.RequestHandler):
    def get(self):
        joke = get_random_joke()
        words = joke.text.split()
        print(words)


def get_random_joke():
    headers = {'user-agent': 'ewehner', 'Accept': 'text/plain'}
    return requests.get("https://icanhazdadjoke.com/", headers=headers)



if __name__ == "__main__":
    static_url_prefix = "/static/"
    dad_jokes = tornado.web.Application([
        (r"/", MainHandler),
        (r"/markov", BuildAJokeHandler)
    ], debug=True)

    logging.warning('DadJokes is now listening on port 8888...')
    dad_jokes.listen(8888)
    tornado.ioloop.IOLoop.current().start()