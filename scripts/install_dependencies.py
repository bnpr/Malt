import os, subprocess, sys, shutil, stat

current_dir = os.path.dirname(os.path.realpath(__file__))

malt_folder = os.path.join(current_dir, '..', 'Malt')

try:
    subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
except:
    subprocess.check_call([sys.executable, '-m', 'ensurepip'])
    os.environ.pop("PIP_REQ_TRACKER", None)

py_version = str(sys.version_info[0])+str(sys.version_info[1])
malt_dependencies_path = os.path.join(malt_folder, '.Dependencies-{}'.format(py_version))
dependencies = ['glfw', 'PyOpenGL', 'PyOpenGL_accelerate', 'Pyrr', 'psutil', 'xxhash']
for dependency in dependencies:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', dependency, '--target', malt_dependencies_path])
    except:
        print('ERROR: pip install {} failed.'.format(dependency))
        import traceback
        traceback.print_exc()


from distutils.dir_util import copy_tree
copy_tree(os.path.join(current_dir, 'PatchDependencies'), malt_dependencies_path) 

#make sure mcpp has executable permissions
for str in ['Linux', 'Darwin']:
    mcpp = os.path.join(malt_dependencies_path, f'mcpp-{str}')
    os.chmod(mcpp, os.stat(mcpp).st_mode | stat.S_IEXEC)

#Remove numpy since Blender already ships with it
#Remove bin to avoid AVs false positives
for e in os.listdir(malt_dependencies_path):
    if e.startswith('numpy') or e == 'bin':
        shutil.rmtree(os.path.join(malt_dependencies_path, e))


#subprocess.check_call([sys.executable, os.path.join(current_dir, 'get_glslang.py')])

