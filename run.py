#!/usr/bin/env python3.5

import sys

from server.app import main as app
from server.samples_server import main as samples_server
from server.setup import main as setup_server


def strip_first_argument():
    sys.argv = [sys.argv[0]] + sys.argv[2:]


def main():
    subject = sys.argv[1]
    if subject == 'app':
        strip_first_argument()
        app()
    elif subject == 'samples_server':
        strip_first_argument()
        samples_server()
    elif subject == 'setup_server':
        strip_first_argument()
        setup_server()
    else:
        samples_server()


if __name__ == '__main__':
    main()
