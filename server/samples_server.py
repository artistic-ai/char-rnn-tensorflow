#!/usr/bin/env python3.5

import argparse
import aiohttp_jinja2
from aiohttp import web
import jinja2
import os

from config import load_config, get_absolute_path
from server.web_utils import setup_logging
import server.samples_tasks as samples_tasks
import server.db as db


SERVER_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(SERVER_ROOT, 'static')


async def samples_handler(request):
    generations = await db.get_samples(request.app)
    sample_index = request.match_info.get('index')

    # Respond with all generations if index omitted
    if sample_index is None:
        return web.json_response(generations)
    else:
        sample_index = int(sample_index)

    if sample_index >= len(generations) or sample_index < -len(generations):
        raise web.HTTPNotFound()

    return web.json_response(generations[sample_index])


@aiohttp_jinja2.template('samples_index.html')
async def index_handler(request):
    samples = await db.get_samples(request.app)
    if request.app['reverse_samples']:
        samples = reversed(samples)

    return {
        'samples': samples,
        'title': request.app['title'],
        'reload_text': request.app['reload_text'],
        'samples_url': request.app.router['samples'].url_for(),
        'reverse_samples': request.app['reverse_samples']
    }


def get_args(config):
    dataset_names = config['dataset_names']
    model_names = config['model_names']

    parser = argparse.ArgumentParser(description='Generate and serve samples for selected model.')
    parser.add_argument('--dataset', type=str,
                        choices=dataset_names, required=True,
                        help='name of dataset to use [%s]' % ', '.join(dataset_names))
    parser.add_argument('--model', type=str,
                        choices=model_names, required=True,
                        help='name of model to sample [%s]' % ', '.join(model_names))
    parser.add_argument('--reload_model', type=int, default=config['server']['reload_model'],
                        help='timeout for model reload')
    parser.add_argument('--reload_text', type=int, default=config['server']['reload_text'],
                        help='timeout for text reload')
    parser.add_argument('--port', type=int, default=config['server']['port'],
                        help='port to bind to')
    parser.add_argument('--reverse_samples', default=config['server']['reverse_samples'], action='store_true',
                        help='reverse samples order')
    parser.add_argument('--clean', default=False, action='store_true',
                        help='clean previous generations')

    return parser.parse_args()


def main():
    config = load_config()
    args = get_args(config)
    setup_logging(config, module='samples_server')

    dataset_name = args.dataset
    model_name = args.model
    model_url = '%s/%s' % (dataset_name, model_name)

    app = web.Application()
    app['title'] = 'Texts generated from model %s' % model_url
    app['model_url'] = model_url
    app['model_dir'] = get_absolute_path(config['models'][dataset_name][model_name]['path'])
    app['reload_model'] = args.reload_model
    app['reload_text'] = args.reload_text
    app['reverse_samples'] = args.reverse_samples
    app['redis'] = config['server']['redis'].copy()
    app['redis']['generations_key'] = app['redis']['generations_key'].format(model_url=model_url)

    app.router.add_get('/', index_handler, name='index')
    app.router.add_get('/samples', samples_handler, name='samples')
    app.router.add_get('/samples/{index}', samples_handler, name='sample_by_index')
    app.router.add_static('/static',
                          path=STATIC_ROOT,
                          name='static')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(STATIC_ROOT))

    app.on_startup.append(db.connect_to_redis)
    app.on_startup.append(samples_tasks.start_background_tasks)
    app.on_cleanup.append(samples_tasks.cleanup_background_tasks)
    app.on_cleanup.append(db.close_redis)

    web.run_app(app, port=args.port)


if __name__ == '__main__':
    main()
