# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 


LOG_MODES = [
    'NONE',
    'USER',
    'WARNING',
    'DEBUG',
    'FULL'
]

LOG_MODE = 'USER'

def log(mode, *messages):
    if LOG_MODES.index(mode) <= LOG_MODES.index(LOG_MODE):
        for message in messages:
            print(message)

