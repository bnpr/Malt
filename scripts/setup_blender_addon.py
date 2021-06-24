import os, sys, platform, subprocess, shutil, pathlib

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--scripts-folder', type=pathlib.Path, help='Create a symlink pointing to the addon.')
parser.add_argument('--copy-modules', action='store_true', help='Copy Malt and Bridge instead of making a symlink. (Needed for zipping in Linux)')
ARGS = parser.parse_args()

current_dir = os.path.dirname(os.path.realpath(__file__))
main_dir = os.path.realpath(os.path.join(current_dir, '..'))

blender_malt_folder = os.path.join(main_dir, 'BlenderMalt')
bridge_folder = os.path.join(main_dir, 'Bridge')
malt_folder = os.path.join(main_dir, 'Malt')

def build_lib(path):
    try:
        subprocess.check_call([sys.executable, 'build.py'], cwd=path)
        shutil.rmtree(os.path.join(path, '.build'))
    except:
        import traceback
        traceback.print_exc()

build_lib(os.path.join(blender_malt_folder, 'CBlenderMalt'))
build_lib(os.path.join(bridge_folder, 'ipc'))

subprocess.check_call([sys.executable, os.path.join(current_dir, 'install_dependencies.py')])

def ensure_dir(path):
    if os.path.exists(path) == False:
        os.mkdir(path)

def make_link(point_from, point_to):
    if os.path.exists(point_from):
        print('Already linked:', point_from, '<--->', point_to)
        return
    if platform.system() == 'Windows':
        import _winapi
        _winapi.CreateJunction(point_to, point_from)
    else:
        os.symlink(point_to, point_from, True)

def make_copy(copy_to, copy_from):
    from distutils.dir_util import copy_tree
    copy_tree(copy_from, copy_to)

import_path = os.path.join(blender_malt_folder, '.MaltPath')
ensure_dir(import_path)

setup_modules = make_link
if ARGS.copy_modules:
    setup_modules = make_copy

setup_modules(os.path.join(import_path, 'Malt'), os.path.join(main_dir, 'Malt'))
setup_modules(os.path.join(import_path, 'Bridge'), os.path.join(main_dir, 'Bridge'))

if ARGS.scripts_folder:
    addons_folder = os.path.join(ARGS.scripts_folder, 'addons')
    ensure_dir(addons_folder)
    make_link(os.path.join(addons_folder, 'BlenderMalt'), blender_malt_folder)

