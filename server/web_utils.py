import os

import logging
from logging import config as logging_config
import sys
import traceback

from config import get_absolute_path


def setup_logging(config, module=None):
    logger = logging.getLogger('exceptions')

    def exceptions_handler(etype, value, tb):
        msg = ''.join(traceback.format_exception(etype, value, tb))
        logger.exception(msg)
        traceback.print_exception(etype, value, tb)

    sys.excepthook = exceptions_handler

    for _, handler in config['server']['logging']['handlers'].items():
        if 'filename' in handler:
            dirname = os.path.dirname(handler['filename'])
            filename = os.path.basename(handler['filename'])

            if module is not None:
                filename = '{module}-{filename}'.format(module=module, filename=filename)

            handler['filename'] = get_absolute_path(config['server']['dirs']['logs'], dirname, filename)

    logging_config.dictConfig(config['server']['logging'])
