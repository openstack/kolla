#!/usr/bin/python

import os
import sys
import argparse
import yaml
import logging

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('input', nargs='*')
    return p.parse_args()

def main():
    args = parse_args()
    logging.basicConfig()
    res = 0

    for filename in args.input:
        with open(filename) as fd:
            try:
                data = yaml.load(fd)
            except yaml.error.YAMLError as error:
                res = 1
                logging.error('%s failed validation: %s',
                              filename, error)

    sys.exit(res)

if __name__ == '__main__':
    main()


