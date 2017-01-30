#!/usr/bin/env python3.5

from jinja2 import Template

from config import load_config, get_absolute_path
from utils import prepare_dir


def main():
    config = load_config()
    nginx_config = config['server']['nginx']
    upstream = '{host}:{port}'.format(host=nginx_config['upstream']['host'],
                                      port=nginx_config['upstream']['port'])
    logdir = get_absolute_path(config['server']['dirs']['logs'])
    cachedir = get_absolute_path(config['server']['dirs']['cache'])
    datadir = get_absolute_path(config['server']['dirs']['samples'])
    config_tmpl = get_absolute_path(nginx_config['config_template'])
    config_file = get_absolute_path(nginx_config['config_file'])

    prepare_dir(logdir)
    prepare_dir(cachedir)
    prepare_dir(datadir)

    with open(config_tmpl, 'r') as infile:
        template = Template(infile.read())
        nginx_conffile = template.render(port=nginx_config['port'], upstream=upstream,
                                         logdir=logdir, cachedir=cachedir,
                                         cache_size=nginx_config['cache']['size'],
                                         cache_time=nginx_config['cache']['time'])

        with open(config_file, 'w') as outfile:
            outfile.write(nginx_conffile)
            print('Create nginx config at %s' % config_file)


if __name__ == '__main__':
    main()
