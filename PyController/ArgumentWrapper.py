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


CONTROLLER_BUTTONS = ['BTN_0', 'BTN_1', 'BTN_2', 'BTN_3', 'BTN_4', 'BTN_5', 'BTN_6', 'BTN_7', 'BTN_8', 'BTN_9',
                      'BTN_A', 'BTN_B', 'BTN_BACK', 'BTN_BASE', 'BTN_BASE2', 'BTN_BASE3', 'BTN_BASE4', 'BTN_BASE5',
                      'BTN_BASE6', 'BTN_C', 'BTN_DEAD', 'BTN_DIGI', 'BTN_DPAD_DOWN', 'BTN_DPAD_LEFT', 'BTN_DPAD_RIGHT',
                      'BTN_DPAD_UP', 'BTN_EAST', 'BTN_EXTRA', 'BTN_FORWARD', 'BTN_GAMEPAD', 'BTN_GEAR_DOWN',
                      'BTN_GEAR_UP', 'BTN_JOYSTICK', 'BTN_LEFT', 'BTN_MIDDLE', 'BTN_MISC', 'BTN_MODE', 'BTN_MOUSE',
                      'BTN_NORTH', 'BTN_PINKIE', 'BTN_RIGHT', 'BTN_SELECT', 'BTN_SIDE', 'BTN_SOUTH', 'BTN_START',
                      'BTN_STYLUS', 'BTN_STYLUS2', 'BTN_STYLUS3', 'BTN_TASK', 'BTN_THUMB', 'BTN_THUMB2', 'BTN_THUMBL',
                      'BTN_THUMBR', 'BTN_TL', 'BTN_TL2', 'BTN_TOOL_AIRBRUSH', 'BTN_TOOL_BRUSH', 'BTN_TOOL_DOUBLETAP',
                      'BTN_TOOL_FINGER', 'BTN_TOOL_LENS', 'BTN_TOOL_MOUSE', 'BTN_TOOL_PEN', 'BTN_TOOL_PENCIL',
                      'BTN_TOOL_QUADTAP', 'BTN_TOOL_QUINTTAP', 'BTN_TOOL_RUBBER', 'BTN_TOOL_TRIPLETAP', 'BTN_TOP',
                      'BTN_TOP2', 'BTN_TOUCH', 'BTN_TR', 'BTN_TR2', 'BTN_TRIGGER', 'BTN_TRIGGER_HAPPY',
                      'BTN_TRIGGER_HAPPY1', 'BTN_TRIGGER_HAPPY10', 'BTN_TRIGGER_HAPPY11', 'BTN_TRIGGER_HAPPY12',
                      'BTN_TRIGGER_HAPPY13', 'BTN_TRIGGER_HAPPY14', 'BTN_TRIGGER_HAPPY15', 'BTN_TRIGGER_HAPPY16',
                      'BTN_TRIGGER_HAPPY17', 'BTN_TRIGGER_HAPPY18', 'BTN_TRIGGER_HAPPY19', 'BTN_TRIGGER_HAPPY2',
                      'BTN_TRIGGER_HAPPY20', 'BTN_TRIGGER_HAPPY21', 'BTN_TRIGGER_HAPPY22', 'BTN_TRIGGER_HAPPY23',
                      'BTN_TRIGGER_HAPPY24', 'BTN_TRIGGER_HAPPY25', 'BTN_TRIGGER_HAPPY26', 'BTN_TRIGGER_HAPPY27',
                      'BTN_TRIGGER_HAPPY28', 'BTN_TRIGGER_HAPPY29', 'BTN_TRIGGER_HAPPY3', 'BTN_TRIGGER_HAPPY30',
                      'BTN_TRIGGER_HAPPY31', 'BTN_TRIGGER_HAPPY32', 'BTN_TRIGGER_HAPPY33', 'BTN_TRIGGER_HAPPY34',
                      'BTN_TRIGGER_HAPPY35', 'BTN_TRIGGER_HAPPY36', 'BTN_TRIGGER_HAPPY37', 'BTN_TRIGGER_HAPPY38',
                      'BTN_TRIGGER_HAPPY39', 'BTN_TRIGGER_HAPPY4', 'BTN_TRIGGER_HAPPY40', 'BTN_TRIGGER_HAPPY5',
                      'BTN_TRIGGER_HAPPY6', 'BTN_TRIGGER_HAPPY7', 'BTN_TRIGGER_HAPPY8', 'BTN_TRIGGER_HAPPY9',
                      'BTN_WEST', 'BTN_WHEEL', 'BTN_X', 'BTN_Y', 'BTN_Z']


def getArguments():
    my_parser = argparse.ArgumentParser(prog='PyController',
                                        description='This is a game pad key mapping tool.',
                                        epilog='Game on!')

    my_parser.version = 'Pre-Release Alpha 7'
    my_parser.add_argument('-v', action='count', dest='verbosity', default=0,
                           help='Overrides the main.yaml loglevel. -v = WARNING, -vv = INFO, -vvv = DEBUG')
    my_parser.add_argument('--version', action='version')

    my_parser.add_argument('-c', '--config',
                           action='store',
                           type=str,
                           dest='config',
                           default='main.yaml',
                           help="Overrides the default configuration file 'main.yaml'.")

    my_parser.add_argument('--show-config-path',
                           action='store_true',
                           dest='showconfigpath',
                           default=False,
                           help="Shows the location of PyControllers main.yaml config file.")

    my_parser.add_argument('--print-classic-keys',
                           action='store_true',
                           default=False,
                           dest='print_classic_keys',
                           help='Prints a list of classic keys found on a standard QWERTY keyboard. As well possible'
                                'other key types.')

    my_parser.add_argument('--print-controller-buttons',
                           action='store_true',
                           default=False,
                           dest='print_controller_buttons',
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
