#!/usr/bin/env python

from __future__ import print_function

import argparse
import urllib
import os
import zipfile

from config import load_config
from sample import sample
from train import train


CONFIG = load_config()


def prepare_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_from_url(url, dest):
    print('Downloading %s to %s...' % (url, dest))
    urllib.urlretrieve(url, dest)


def unzip_file(src, dest):
    ref = zipfile.ZipFile(src, 'r')
    ref.extractall(dest)
    ref.close()


def download_source(source, dest):
    # Download and extract zip file
    if source['type'] == 'zipfile':
        tmpfile = os.path.join(dest, '_tmpfile.zip')
        download_from_url(source['url'], tmpfile)
        unzip_file(tmpfile, dest)
        os.remove(tmpfile)
    else:
        raise ValueError('Source type "%s" is not supported' % source['type'])


def download(datasets):
    prepare_dir(CONFIG['dirs']['data'])
    prepare_dir(CONFIG['dirs']['models'])

    for dataset in CONFIG['datasets']:
        if dataset['name'] in datasets:
            dataset_dir = dataset['path']
            # Skip dataset loading if dataset directory exists
            if os.path.exists(dataset_dir):
                print('Skipping dataset %s since directory already exists'
                      % dataset['name'])
            else:
                prepare_dir(dataset_dir)
                print('Downloading dataset %s' % dataset['name'])
                for source in dataset['sources']:
                    download_source(source, dataset_dir)

            # Load pre-trained models
            if 'models' in dataset:
                for model in dataset['models']:
                    model_dir = model['path']
                    if os.path.exists(model_dir):
                        print('Skipping model %s of %s since directory already exists'
                              % (model['name'], dataset['name']))
                    else:
                        prepare_dir(model_dir)
                        # Download and extract zip file
                        if 'source' in model:
                            print('Downloading model %s for dataset %s' % (model['name'], dataset['name']))
                            download_source(model['source'], model_dir)


def train_model(dataset, model):
    params = {
        'data_dir': dataset['path'],
        'save_dir': model['path']
    }
    # Initialise from pretrained model if exists
    if 'source' in model and os.path.exists(params['save_dir']):
        params['init_from'] = params['save_dir']
    # Add non-default model parameters from config
    if 'params' in model:
        params.update(model['params'])

    # Train RNN model
    print('Training model %s for dataset %s' % (model['name'], dataset['name']))
    train(**params)


def get_sample(dataset, model):
    params = {
        'save_dir': model['path']
    }

    # Get sample
    print('Getting sample for model %s of dataset %s' % (model['name'], dataset['name']))
    print(sample(**params))


def __get_dataset_and_model(args, dataset_name):
    dataset = [d for d in CONFIG['datasets'] if d['name'] == dataset_name][0]
    if args.model:
        model = [m for m in dataset['models']]
        if len(model) != 1:
            print('Model "%s" is not specified for dataset "%s"' % (model['name'], dataset['name']))
            exit(-1)
    else:
        model = dataset.get('models', [{'name': dataset_name}])[0]

    return dataset, model


def main():
    dataset_names = [d['name'] for d in CONFIG['datasets']]

    parser = argparse.ArgumentParser(description='Download dataset for RNN Tensorflow.')
    parser.add_argument('--datasets', metavar='N', type=str, nargs='+',
                        choices=dataset_names, default=[],
                        help='name of dataset to download [%s]' % ', '.join(dataset_names))
    parser.add_argument('--datasets-all', default=False, action='store_true')
    parser.add_argument('--train', type=str, choices=dataset_names, default=None,
                        help='name of dataset to train on [%s]' % ', '.join(dataset_names))
    parser.add_argument('--sample', type=str, choices=dataset_names, default=None,
                        help='name of dataset to take sample for [%s]' % ', '.join(dataset_names))
    parser.add_argument('--model', type=str, default=None,
                        help='model to train or test')

    args = parser.parse_args()

    # Download all datasets
    if args.datasets_all:
        args.datasets = dataset_names
    # Download specific datasets
    if args.datasets:
        download(args.datasets)
    # Train specific model
    elif args.train:
        dataset, model = __get_dataset_and_model(args, args.train)
        train_model(dataset, model)
    # Get sample from trained model
    elif args.sample:
        dataset, model = __get_dataset_and_model(args, args.sample)
        get_sample(dataset, model)
    # Invalid parameters
    else:
        parser.print_help()
        exit(-1)


if __name__ == '__main__':
    main()
