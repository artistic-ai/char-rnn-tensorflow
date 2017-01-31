#!/usr/bin/env python3.5

from jinja2 import Template

from config import load_config, get_absolute_path
from utils import prepare_dir


def setup_web_servers(config):
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


def setup_redis(config):
    redis_config = config['redis']

    port = redis_config['port']

    logdir = get_absolute_path(redis_config['dirs']['logs'])
    logfile = get_absolute_path(logdir, redis_config['logfile'])

    prepare_dir(logdir)

    config_tmpl = get_absolute_path(redis_config['config_template'])
    config_file = get_absolute_path(redis_config['config_file'])

    db_dir = redis_config['dirs']['db']
    db_file = redis_config['db_file']

    with open(config_tmpl, 'r') as infile:
        template = Template(infile.read())
        nginx_conffile = template.render(port=port, db_dir=db_dir, db_file=db_file, logfile=logfile)

        with open(config_file, 'w') as outfile:
            outfile.write(nginx_conffile)
            print('Create redis config at %s' % config_file)


def main():
    config = load_config()
    setup_web_servers(config)
    setup_redis(config)


if __name__ == '__main__':
    main()
