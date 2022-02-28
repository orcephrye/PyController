#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description:


import argparse

CLASSIC_KEYBOARD = ['KEY_ESC', 'KEY_1', 'KEY_2', 'KEY_3', 'KEY_4', 'KEY_5', 'KEY_6', 'KEY_7', 'KEY_8', 'KEY_9', 'KEY_0',
                    'KEY_MINUS', 'KEY_EQUAL', 'KEY_BACKSPACE', 'KEY_TAB', 'KEY_Q', 'KEY_W', 'KEY_E', 'KEY_R', 'KEY_T',
                    'KEY_Y', 'KEY_U', 'KEY_I', 'KEY_O', 'KEY_P', 'KEY_LEFTBRACE', 'KEY_RIGHTBRACE', 'KEY_ENTER',
                    'KEY_LEFTCTRL', 'KEY_A', 'KEY_S', 'KEY_D', 'KEY_F', 'KEY_G', 'KEY_H', 'KEY_J', 'KEY_K', 'KEY_L',
                    'KEY_SEMICOLON', 'KEY_APOSTROPHE', 'KEY_GRAVE', 'KEY_LEFTSHIFT', 'KEY_BACKSLASH', 'KEY_Z', 'KEY_X',
                    'KEY_C', 'KEY_V', 'KEY_B', 'KEY_N', 'KEY_M', 'KEY_COMMA', 'KEY_DOT', 'KEY_SLASH', 'KEY_RIGHTSHIFT',
                    'KEY_KPASTERISK', 'KEY_LEFTALT', 'KEY_SPACE', 'KEY_CAPSLOCK', 'KEY_F1', 'KEY_F2', 'KEY_F3',
                    'KEY_F4', 'KEY_F5', 'KEY_F6', 'KEY_F7', 'KEY_F8', 'KEY_F9', 'KEY_F10', 'KEY_NUMLOCK',
                    'KEY_SCROLLLOCK', 'KEY_KP7', 'KEY_KP8', 'KEY_KP9', 'KEY_KPMINUS', 'KEY_KP4', 'KEY_KP5', 'KEY_KP6',
                    'KEY_KPPLUS', 'KEY_KP1', 'KEY_KP2', 'KEY_KP3', 'KEY_KP0', 'KEY_KPDOT', 'KEY_ZENKAKUHANKAKU',
                    'KEY_102ND', 'KEY_F11', 'KEY_F12', 'KEY_RO', 'KEY_KATAKANA', 'KEY_HIRAGANA', 'KEY_HENKAN',
                    'KEY_KATAKANAHIRAGANA', 'KEY_MUHENKAN', 'KEY_KPJPCOMMA', 'KEY_KPENTER', 'KEY_RIGHTCTRL',
                    'KEY_KPSLASH', 'KEY_SYSRQ', 'KEY_RIGHTALT', 'KEY_HOME', 'KEY_UP', 'KEY_PAGEUP', 'KEY_LEFT',
                    'KEY_RIGHT', 'KEY_END', 'KEY_DOWN', 'KEY_PAGEDOWN', 'KEY_INSERT', 'KEY_DELETE', 'KEY_KPEQUAL',
                    'KEY_PAUSE', 'KEY_KPCOMMA', 'KEY_HANJA', 'KEY_YEN', 'KEY_LEFTMETA', 'KEY_RIGHTMETA', 'KEY_COMPOSE',
                    'KEY_STOP', 'KEY_AGAIN', 'KEY_PROPS', 'KEY_UNDO', 'KEY_FRONT', 'KEY_COPY', 'KEY_OPEN', 'KEY_PASTE',
                    'KEY_FIND', 'KEY_CUT', 'KEY_KPLEFTPAREN', 'KEY_KPRIGHTPAREN']


def getArguments():
    my_parser = argparse.ArgumentParser(prog='PyController',
                                        description='This is a game pad key mapping tool.',
                                        epilog='Game on!')

    my_parser.version = 'Pre-Release Alpha 5'
    my_parser.add_argument('-v', action='count', dest='verbosity', default=0,
                           help='Overrides the main.yaml loglevel. -v = WARNING, -vv = INFO, -vvv = DEBUG')
    my_parser.add_argument('--version', action='version')

    my_parser.add_argument('-c', '--config',
                           action='store',
                           type=str,
                           dest='config',
                           default='main.yaml',
                           help="Overrides the default configuration file 'main.yaml'.")

    my_parser.add_argument('--print-classic-keys',
                           action='store_true',
                           default=False,
                           dest='print_classic_keys',
                           help='Prints a list of classic keys found on a standard QWERTY keyboard. As well possible'
                                'other key types.')

    my_parser.add_argument('--list-devices',
                           action='store_true',
                           default=False,
                           dest='list_devices',
                           help='Tells PyController to list accessible devices under /dev/input/')

    my_parser.add_argument('--print-capabilities',
                           action='store',
                           type=str,
                           default='',
                           dest='print_capabilities',
                           help="Attempts to provide the specified device's available keys. DeviceID format is "
                                "vendorID:productID which can be found using the '--list-devices' flag")

    my_parser.add_argument('--print-key-presses',
                           action='store',
                           type=str,
                           default='',
                           dest='print_key_presses',
                           help="Attempts to print out key presses from the specified device as vendorID:productID "
                                "which can be found using the '--list-devices' flag")

    return my_parser.parse_args()
