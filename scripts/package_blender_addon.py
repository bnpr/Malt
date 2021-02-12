import os, sys, platform, subprocess, shutil

current_dir = os.path.dirname(os.path.realpath(__file__))
main_dir = os.path.realpath(os.path.join(current_dir, '..'))

blender_malt_folder = os.path.join(main_dir, 'BlenderMalt')
bridge_folder = os.path.join(main_dir, 'Bridge')
malt_folder = os.path.join(main_dir, 'Malt')

def build_lib(path):
    subprocess.check_call([sys.executable, 'build.py'], cwd=path)
    shutil.rmtree(os.path.join(path, '.build'))

build_lib(os.path.join(blender_malt_folder, 'CBlenderMalt'))
build_lib(os.path.join(bridge_folder, 'ipc'))

subprocess.check_call([sys.executable, os.path.join(current_dir, 'install_dependencies.py')])

def make_link(point_from, point_to):
    if os.path.exists(point_from):
        print('Already linked:', point_from, '<--->', point_to)
        return
    if platform.system() == 'Windows':
        import _winapi
        _winapi.CreateJunction(point_to, point_from)
    else:
        from distutils.dir_util import copy_tree
        copy_tree(point_to, point_from)
        #Symlinks don't work ?!?!?
        #os.symlink(point_to, point_from, True)

import_path = os.path.join(blender_malt_folder, '.MaltPath')
if os.path.exists(import_path) == False:
    os.mkdir(import_path)
make_link(os.path.join(import_path, 'Malt'), os.path.join(main_dir, 'Malt'))
make_link(os.path.join(import_path, 'Bridge'), os.path.join(main_dir, 'Bridge'))

