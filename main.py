import datetime
import locale
import logging
import os
import re
import string

from googlemaps import exceptions as ge
from gdir.cctld import CCTLDS
from gdir.directions import Directions
from gdir.directions import Directions
from gdir.directions import NotFoundError

from werkzeug.wrappers import Request, Response
from werkzeug.utils import escape

MAX_FIELD_LENGTH = 1024

@Request.application
def app(request):
    logger = logging.getLogger('gdir')

    text = '<?xml version="1.0" encoding="utf-8"?>\n' \
           '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n' \
           '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n' \
           '<head>\n' \
           '<title>Results</title>\n' \
           '</head>\n' \
           '<body>\n' \

    form = {}
    form['transit_modes'] = [m for m in ('rail', 'train', 'tram', 'subway', 'bus')
                             if request.args.get(m) is not None]
    form['origin'] = request.args.get('origin', '')
    form['destination'] = request.args.get('destination', '')
    form['mode_of_travel'] = request.args.get('mode_of_travel', '')
    form['country'] = request.args.get('country', '')
    form['multiple_routes'] = True if request.args.get('multiple_routes') is not None else False
    form['walking_substeps'] = True if request.args.get('walking_substeps') is not None else False

    try:
        if (len(form['country']) > 0 and form['country'] not in CCTLDS):
            raise ValueError('Invalid country specified.')
        if len(form['origin']) == 0 | len(form['destination']) == 0:
            raise ValueError('Both start location and end location are required fields.')
        if form['mode_of_travel'] not in ('transit', 'driving', 'bicycling', 'walking'):
            raise ValueError('Invalid mode of travel specified.')
        for v in form.values():
            if isinstance(v, str) and len(v) > MAX_FIELD_LENGTH:
                raise ValueError('Maximum field length exceeded.')

        region = form['country'] if len(form['country']) > 0 else None
        language = 'en_GB' if form['country'] in ('gb', 'uk') else locale.getdefaultlocale()[0]


        directions = Directions(form['origin'], form['destination'],
                                form['mode_of_travel'],
                                form['transit_modes'],
                                departure_time=None,
                                arrival_time=None,
                                region=region,
                                alternatives=form['multiple_routes'],
                                maps_key=os.environ['GOOGLE_MAPS_API_KEY'],
                                language=language,
                                display_copyrights=True)
        results = directions.to_str(form['walking_substeps'], text_wrap=False)
        text += parse(results) + '\n'

        logger.info('Returned result successfully.')
    except (ValueError, NotFoundError, ge.ApiError, ge.TransportError, ge.HTTPError,
            ge.Timeout) as e:
        # Invalid argument
        # Origin/destination not found
        # Api Error
        # Transport Error
        # HTTP Error
        # Timeout Error
        text += str(e) + '\n'

        logger.info('Failed to return result: {}'.format(e))

    text += '</body>\n' \
            '</html>'
    text = strip_ansi_escape_sequences(text)
    text = str(text).encode('ascii', 'xmlcharrefreplace').decode()

    return Response(text, mimetype='text/html')

def strip_ansi_escape_sequences(text):
    pattern = re.compile(r'\x1B\[\d+(;\d+){0,2}m')
    return pattern.sub('', text)

def parse(results):
    text = ''
    routes, copyright = results.split('\n\n\n')

    text += '<h1>Results</h1>\n'
    routes = routes.split('\n\n')
    for route in routes:
        lines = route.split('\n')
        lines = [line.lstrip() for line in lines]

        text += '<h2>{}</h2>\n'.format(lines.pop(0))

        steps = []
        for line in lines:
            left_col, *right_col = line.split(' ')
            right_col = ' '.join(right_col)

            if left_col.isnumeric():
                if 'substeps' not in steps[-1].keys():
                    steps[-1]['substeps'] = []
                steps[-1]['substeps'].append(right_col)
            else:
                steps.append({'step': '<strong>{}</strong> {}'.format(left_col, right_col)})

        text += '<ul>\n'
        for step in steps:
            text += '<li>{}\n'.format(step['step'])
            if 'substeps' in step.keys():
                text += '<ol>\n'
                for substep in step['substeps']:
                    text += '<li>{}</li>\n'.format(substep)
                text += '</ol>\n'
            text += '</li>\n'
        text += '</ul>\n'

    text += '<h1>Transport and Copyright Notices</h1>\n'
    copyright = copyright.replace('\n', '<br/>')
    text += '<p>{}</p>\n'.format(copyright)

    return text

if __name__ == '__main__':
    # This entry point is intended for local development only.
    # Point your browser at http://localhost:8000/index.html

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    from werkzeug.serving import run_simple
    run_simple('localhost', 8000,
               app, use_debugger=True,
               use_reloader=True,
               static_files={'/index.html': 'index.html'})
