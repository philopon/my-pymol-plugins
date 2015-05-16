import os
from pymol import cmd

def Windows_Desktop():
    drive = os.getenv('HOMEDRIVE')
    if not drive: return
    path  = os.getenv('HOMEPATH')
    if not path: return
    return drive + path + '\\Desktop'

def _Nix_Desktop():
    home = os.getenv('HOME')
    if not home: return
    return os.path.join(home, 'Desktop')

def pathes(prefix, filetype):
    yield prefix + '.' + filetype

    i = 1
    while True:
        yield '{}-{}.{}'.format(prefix, i, filetype)
        i = i + 1

def save_image(
        width = 1920,
        height = 1080,
        selection = '(all)',
        format = 'png',
        state = -1,
        prefix = os.path.join(Windows_Desktop() or _Nix_Desktop(), 'PyMOL'),
        renderer = -1,
        shift = 0.0):
    cmd.ray(width, height, renderer, shift)

    for path in pathes(prefix, format):
        if not os.path.exists(path):
            cmd.save(path, selection, state, format)
            break

def __init_plugin__(self = None):
    cmd.extend('image', save_image)
