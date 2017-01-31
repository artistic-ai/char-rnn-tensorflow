#!/usr/bin/env python3.5

import argparse
import aiohttp_jinja2
from aiohttp import web
import jinja2
import os

from config import load_config, get_absolute_path
from server.web_utils import setup_logging
from server.app_tasks import start_samples_servers, terminate_samples_servers, get_remote_samples
import server.db as db


SERVER_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(SERVER_ROOT, 'static')


def get_args(config):
    model_urls = [m['url'] for m in config['server']['models']]

    parser = argparse.ArgumentParser(description='Manage and serve multiple samples.')
    parser.add_argument('--models', metavar='N', type=str, nargs='+',
                        choices=model_urls, default=model_urls,
                        help='name of dataset to download [%s]' % ', '.join(model_urls))
    parser.add_argument('--reverse_samples', default=config['server']['reverse_samples'], action='store_true',
                        help='reverse samples order')
    parser.add_argument('--port', type=int, default=config['server']['port'],
                        help='port to bind to')

    return parser.parse_args()


@aiohttp_jinja2.template('app_index.html')
async def index_handler(request):
    samples_pages = []
    for model in request.app['models']:
        dataset_name, model_name = model['url'].split('/')
        url = request.app.router['samples_page'].url_for(dataset=dataset_name, model=model_name)
        samples_pages.append({
            'title': model['title'],
            'url': url
        })
    return {'samples_pages': samples_pages}


@aiohttp_jinja2.template('samples_index.html')
async def samples_page_handler(request):
    dataset_name =request.match_info['dataset']
    model_name =request.match_info['model']
    model_url = '%s/%s' % (dataset_name, model_name)

    samples = await get_remote_samples(request.app, model_url)

    if request.app['reverse_samples']:
        samples = reversed(samples)

    return {
        'samples': samples,
        'title': 'Texts generated from model %s' % model_url,
        'reload_text': request.app['reload_text'],
        'samples_url': request.app.router['samples'].url_for(dataset=dataset_name, model=model_name),
        'reverse_samples': request.app['reverse_samples']
    }


async def samples_handler(request):
    dataset_name =request.match_info['dataset']
    model_name =request.match_info['model']
    model_url = '%s/%s' % (dataset_name, model_name)

    samples = await get_remote_samples(request.app, model_url)

    return web.json_response(samples)


def main():
    config = load_config()
    setup_logging(config, module='app')
    args = get_args(config)

    app = web.Application()

    app['models'] = [m for m in config['server']['models'] if m['url'] in args.models]
    app['sample_servers'] = {}
    app['samples_server_script'] = get_absolute_path('run.py')
    app['reload_text'] = config['server']['reload_text']
    app['reverse_samples'] = args.reverse_samples
    app['redis'] = config['server']['redis'].copy()
    app['retrieve_method'] = config['server']['retrieve_method']

    app.router.add_get('/', index_handler, name='index')
    app.router.add_get('/{dataset}/{model}', samples_page_handler, name='samples_page')
    app.router.add_get('/samples/{dataset}/{model}', samples_handler, name='samples')
    app.router.add_static('/static',
                          path=STATIC_ROOT,
                          name='static')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(STATIC_ROOT))

    app.on_startup.append(db.connect_to_redis)
    app.on_startup.append(start_samples_servers)
    app.on_cleanup.append(terminate_samples_servers)
    app.on_cleanup.append(db.close_redis)

    web.run_app(app, port=args.port)


if __name__ == '__main__':
    main()
