# gdir.telae.net
This repository contains the code for [gdir.telae.net](https://gdir.telae.net), a minimalistic directions service. If you are interested in (self-)hosting this service, please read on. If you are a command line user, consider using [gdir](https://github.com/pafoster/gdir), which this service is based on.

## Pre-requisites
The service is implemented as a [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) web application in **Python 3** and [werkzeug](https://werkzeug.palletsprojects.com/en/2.2.x/#). To deploy the service, you will therefore need a web server setup which provides WSGI capabilities. For this, there are [numerous options](https://wsgi.readthedocs.io/en/latest/servers.html). Broadly speaking, the options fall into two categories:
* Web server with modular (or built-in) WSGI capabilities, e.g. Apache + [mod_wsgi](https://modwsgi.readthedocs.io/en/master/)
* Web server → WSGI application server. Both communicate via a gateway protocol such as HTTP, CGI, FastCGI, SCGI, uwsgi.
*Side note: uwsgi is the name of a gateway protocol as well as an [application server](https://uwsgi-docs.readthedocs.io/en/latest/). Other possible WSGI application servers include [flup](https://www.saddi.com/software/flup/), [gunicorn](https://gunicorn.org/), [waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/index.html), ...*

Choose a setup which reflects your needs, security considerations and personal preferences. In UNIX/Linux environments, tools like [supervisord](http://supervisord.org/) may be useful for controlling WSGI application servers.

## Local Development
Local development uses a setup correponding to the first category, namely werkzeug's development web server. For local development,
1. Create a new Python virtual environment
2. `pip install -r requirements.txt`
3. `export GOOGLE_MAPS_API_KEY=your-google-maps-api-key`
4. `python main.py`
5. Point your browser at http://localhost:8000/index.html

## Deploying Using OpenBSD httpd → flup (via FastCGI)
One example setup based on the provided [fastcgi.py](fastcgi.py) is:
1. Create a new Python virtual environment
2. `pip install -r requirements.txt`
3. `pip install flup`
4. Configure httpd to use FastCGI
5. Configure supervisord to execute an instance of flup inside the Python virtual environment
6. Copy [index.html](index.html) to web server's document root

### httpd config
[fastcgi.py](fastcgi.py) implements a FastCGI service bound to localhost port 8000. Relevant httpd config directives are:
```
server "example.com" {

      ... your additional config here ....

        location "/gdir/*" {
                fastcgi {
                        socket tcp localhost 8000
                }
                root "/"
        }
}
```
### supervisord config
```
[program:gdir]
command=/path/to/venv/bin/python /path/to/fastcgi.py
user=www
autostart=true
autorestart=true
stdout_logfile=/var/www/logs/fastcgi.log
redirect_stderr=true
environment=GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here
```
Note: [main.py](main.py) reads from the environment variable `GOOGLE_MAPS_API_KEY`, which in this example is defined in the above supervisord config. Thus, the variable is propagated by supervisord invoking flup. *For alternative setups, a possible pitfall is that CGI environment variables sent via FastCGI are surfaced using the environment variable `FCGI_PARAMS` ([reference](https://serverfault.com/questions/929993/how-does-nginx-pass-environmental-variables-to-fast-cgi-handlers-like-php-fpm)).*
