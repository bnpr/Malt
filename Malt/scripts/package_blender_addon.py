import os, subprocess, sys, shutil

blender_malt_folder = os.path.join('..', 'BlenderMalt')

CBlenderMalt_folder = os.path.join(blender_malt_folder, 'CBlenderMalt')
subprocess.check_call(['python', 'build.py'], cwd=CBlenderMalt_folder)
shutil.rmtree(os.path.join(CBlenderMalt_folder, '.build'))

malt_dependencies_path = os.path.join(blender_malt_folder, 'MaltDependencies')
dependencies = ['PyOpenGL', 'PyOpenGL_accelerate', 'pcpp', 'Pyrr']
subprocess.check_call([sys.executable, '-m', 'pip', 'install', *dependencies, '--target', malt_dependencies_path])

from distutils.dir_util import copy_tree
copy_tree(os.path.join(blender_malt_folder, 'PatchDependencies'), malt_dependencies_path) 

#Remove numpy since Blender already ships with it
for e in os.listdir(malt_dependencies_path):
    if e.startswith('numpy'):
        shutil.rmtree(os.path.join(malt_dependencies_path, e))

copy_tree(os.path.join('..', 'Malt'), os.path.join(blender_malt_folder, 'MaltPath', 'Malt'))

