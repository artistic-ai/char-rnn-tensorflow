import subprocess
import sys

from config import PROJECT_ROOT
from server.server_utils import get_free_tcp_port


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
