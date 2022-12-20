import logging

from flup.server.fcgi import WSGIServer

import main

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel(logging.INFO)
    WSGIServer(main.app, bindAddress=('localhost', 8000)).run()
