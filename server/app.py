import aiohttp_jinja2
import jinja2
from aiohttp import web
import os

from config import load_config, PROJECT_ROOT
from server.background_tasks import start_background_tasks, cleanup_background_tasks


SERVER_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(SERVER_ROOT, 'static')


async def samples_handler(request):
    generations = request.app['text_generations']
    sample_index = request.match_info.get('index')

    # Respond with all generations if index omitted
    if sample_index is None:
        return web.json_response(generations)
    else:
        sample_index = int(sample_index)

    if sample_index >= len(generations) or sample_index not in generations:
        raise web.HTTPNotFound()

    return web.json_response(generations[sample_index])


@aiohttp_jinja2.template('index.html')
async def index_handler(request):
    return {
        'samples': reversed(request.app['text_generations']),
        'title': request.app['title']
    }


def main():
    config = load_config()
    dataset_name = config['server']['dataset']
    model_name = config['server']['model']

    app = web.Application()
    app['title'] = 'Texts generated from model %s/%s' % (dataset_name, model_name)
    app['model_dir'] = os.path.join(PROJECT_ROOT, config['models'][dataset_name][model_name]['path'])
    app['reload_model'] = config['server']['reload_model']
    app['reload_text'] = config['server']['reload_text']
    app['text_generations'] = []

    app.router.add_get('/', index_handler, name='index')
    app.router.add_get('/samples', samples_handler, name='samples')
    app.router.add_get('/samples/{index}', samples_handler, name='sample_by_index')
    app.router.add_static('/static',
                          path=STATIC_ROOT,
                          name='static')

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(STATIC_ROOT))
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    web.run_app(app)


if __name__ == '__main__':
    main()
