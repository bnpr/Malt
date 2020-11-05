import subprocess
import os

src_dir = os.path.abspath(os.path.dirname(__file__))
build_dir = os.path.join(src_dir, '.build') 

try: os.mkdir(build_dir)
except: pass

subprocess.check_call(['cmake', '-A', 'x64', '..'], cwd=build_dir)
subprocess.check_call(['cmake', '--build', '.', '--config', 'Release'], cwd=build_dir)
subprocess.check_call(['cmake', '--install', '.'], cwd=build_dir)