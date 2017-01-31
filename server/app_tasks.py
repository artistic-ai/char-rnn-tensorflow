import subprocess
import sys
from aiohttp import ClientSession

from config import PROJECT_ROOT
from server.server_utils import get_free_tcp_port
import server.db as db


def start_samples_servers(app):
    for model in app['models']:
        model_url = model['url']
        dataset_name, model_name = model_url.split('/')
        port = get_free_tcp_port()
        p = subprocess.Popen([sys.executable,
                              app['samples_server_script'],
                              '--port', str(port),
                              '--dataset', dataset_name,
                              '--model', model_name],
                             cwd=PROJECT_ROOT)

        app['sample_servers'][model_url] = {
            'process': p,
            'port': port
        }


def terminate_samples_servers(app):
    for _, sample_server in app['sample_servers'].items():
        sample_server['process'].terminate()


async def get_remote_samples(app, model_url):
    app.logger.info('Retrieving remote samples for {model_url} by {method}'
                    .format(model_url=model_url, method=app['retrieve_method']))

    if app['retrieve_method'] == 'http':
        sample_server = app['sample_servers'][model_url]
        port = sample_server['port']
        async with ClientSession() as session:
            async with session.get('http://0.0.0.0:%s/samples' % port) as resp:
                return await resp.json()
    elif app['retrieve_method'] == 'redis':
        return await db.get_samples(app, model_url)
