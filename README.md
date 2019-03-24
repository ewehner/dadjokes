A markov-chain Dad-joke generator... for when you need a good joke.

### Runbook:

This is a Python 3.7 application. You can run this locally using the following steps. Note that you will also need to spin up a local redis server (see section 2 below for instructions)

###### Setup and Run Dad Jokes:

1. Install the latest version of Python and pipenv. There are some nice instructions [here].

[here]: https://docs.python-guide.org/starting/install3/osx/

2. Clone this repository to your local environment.

3. cd into the project directory and set up your pipenv environment. There is a nice example of the pipenv install/workflow [here]

[here]: https://pipenv.readthedocs.io/en/latest/basics/#example-pipenv-workflow

4. Spin up the redis server (see below)

5. Begin the service with: 

`pipenv run python dadjokes.py`

###### Spinning up a Redis Server

1. Download redis software, e.g. for mac:

`wget http://download.redis.io/redis-stable.tar.gz`

2. Move file to where you want to install redis and unpack it using:

`tar xvzf redis-stable.tar.gz `

3. Make redis using:

`cd redis-stable`
`make`

4. Check success of compilation with:

`make test`

5. Install redis:

`sudo make install`

This moves the redis server and command line interfaces to /usr/local/bin.

6. cd into the dadjokes project directory and start the redis server with: 

`redis-server`

Note: Make sure the port it runs on matches the port used to initialize it in dadjokes.py

###### Getting some jokes

This application has several endpoints. If you'd like a random, real Dad-joke, you can visit:

`localhost:8888/real`

For a list of all the jokes (say if you're having a bad day and just REALLY need some jokes), use:

`localhost:8888/list`

And if you want a Markov-chain generated joke, go to:

`localhost:8888`

And voila! Prepare to be amused!

`