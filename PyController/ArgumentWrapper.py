#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description:


import argparse

def getArguments():
    my_parser = argparse.ArgumentParser(prog='PyController',
                                        description='This is a game pad key mapping tool.',
                                        epilog='Game on!')

    my_parser.version = 'Alpha 4'
    my_parser.add_argument('-v', action='count', dest='verbosity', default=0,
                           help='Overrides the main.yaml loglevel. -v = WARNING, -vv = INFO, -vvv = DEBUG')
    my_parser.add_argument('--version', action='version')

    my_parser.add_argument('-l', '--list',
                           action='store_true',
                           default=False,
                           dest='list_devices',
                           help='Tells PyController to list accessible devices under /dev/input/')

    my_parser.add_argument('-c', '--config',
                           action='store',
                           type=str,
                           dest='config',
                           default='main.yaml',
                           help="Overrides the default configuration file 'main.yaml'.")

    return my_parser.parse_args()
