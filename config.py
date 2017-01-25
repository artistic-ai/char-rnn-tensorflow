import os
import yaml


PROJECT_ROOT = os.path.dirname(__file__)


def load_config():
    with open(os.path.join(PROJECT_ROOT, 'config.yaml')) as config_file:
        return __set_config_defaults(
            yaml.load(config_file.read())
        )


def __dataset_path(dataset, config):
    return os.path.join(config['dirs']['data'], dataset['name'])


def __model_path(dataset, model, config):
    params = [config['dirs']['models'], dataset['name']]
    if model is not None:
        params.append(model['name'])
    return os.path.join(*params)


def __set_config_defaults(config):
    # Create a k/v registry of models
    config['models'] = {}

    for d in config.get('datasets', []):
        # Add default model to dataset
        if 'models' not in d:
            d['models'] = [{'name': d['name']}]
        # Add path to dataset directory
        if 'path' not in d:
            d['path'] = __dataset_path(d, config)

        # Add root for dataset's models in models registry
        config['models'][d['name']] = {}
        # Index models
        for m in d['models']:
            # Add model to k/v registry
            config['models'][d['name']][m['name']] = m
            # Add link to dataset into model
            m['dataset'] = d
            # Add path to model directory
            if 'path' not in m:
                m['path'] = __model_path(d, m, config)

    # Create lists of models and dataset names
    config['dataset_names'] = [d['name'] for d in config['datasets']]
    config['model_names'] = [m['name'] for d in config['datasets'] for m in d['models']]

    return config
