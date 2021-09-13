import subprocess
import os
import platform

current_dir = os.path.abspath(os.path.dirname(__file__))
build_dir = os.path.join(current_dir, '.build') 

try: os.mkdir(build_dir)
except: pass

if platform.system() == 'Windows': #Multi-config generators, like Visual Studio
    subprocess.check_call(['cmake', '-A', 'x64', '..'], cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=build_dir)
else: #Single-config generators
    subprocess.check_call(['cmake', '..'], cwd=build_dir)
    subprocess.check_call(['cmake', '--build', '.'], cwd=build_dir)

#subprocess.check_call(['cmake', '--install', '.', '--prefix', '.'], cwd=build_dir)
from distutils.dir_util import copy_tree
copy_tree(os.path.join(current_dir, 'bin', 'Release'), current_dir)


