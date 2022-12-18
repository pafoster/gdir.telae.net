# gdir.telae.net
This repository contains the code for [gdir.telae.net](https://gdir.telae.net), a minimalistic directions service. If you are interested in (self-)hosting this service, please read on. If you are a command line user, consider using [gdir](https://github.com/pafoster/gdir), which this service is based on.

# Pre-requisites
The service is implemented as a [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) web application in **Python 3** and [werkzeug](https://werkzeug.palletsprojects.com/en/2.2.x/#). To deploy the service, you will therefore need a web server setup which provides WSGI capabilities. For this, there are [numerous options](https://wsgi.readthedocs.io/en/latest/servers.html). Broadly speaking, the options fall into two categories:
* Web server with modular (or built-in) WSGI capabilities, e.g. Apache + [mod_wsgi](https://modwsgi.readthedocs.io/en/master/)
* Web server + WSGI application server. Both communicate via a gateway protocol such as HTTP, CGI, FastCGI, SCGI, uwsgi.
*Side note: uwsgi is the name of a gateway protocol as well as an [application server](https://uwsgi-docs.readthedocs.io/en/latest/). Other possible WSGI application servers include [flup](https://www.saddi.com/software/flup/), [gunicorn](https://gunicorn.org/), [waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/index.html), ...*

Choose a setup which reflects your needs, security considerations and personal preferences. In UNIX/Linux environments, tools like [supervisord](http://supervisord.org/) may be useful for controlling WSGI application servers.

# Local Development
Local development uses a setup correponding to the first category, namely werkzeug's development web server. For local development,
1. Create a new Python virtual environment
2. `pip install requirements.txt`
3. `python main.py`
4. Point your browser at http://localhost:8000/index.html
