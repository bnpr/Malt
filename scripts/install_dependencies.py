import os, subprocess, sys, shutil

current_dir = os.path.dirname(os.path.realpath(__file__))

malt_folder = os.path.join(current_dir, '..', 'Malt')

malt_dependencies_path = os.path.join(malt_folder, '.Dependencies')
dependencies = ['glfw', 'PyOpenGL', 'PyOpenGL_accelerate', 'pcpp', 'Pyrr']
subprocess.check_call([sys.executable, '-m', 'pip', 'install', *dependencies, '--target', malt_dependencies_path])

from distutils.dir_util import copy_tree
copy_tree(os.path.join(current_dir, 'PatchDependencies'), malt_dependencies_path) 

#Remove numpy since Blender already ships with it
#Remove bin to avoid AVs false positives
for e in os.listdir(malt_dependencies_path):
    if e.startswith('numpy') or e == 'bin':
        shutil.rmtree(os.path.join(malt_dependencies_path, e))

