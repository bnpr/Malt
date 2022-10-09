import os, stat, platform, shutil, zipfile

current_dir = os.path.dirname(os.path.realpath(__file__))
gl_folder = os.path.join(current_dir, '..', 'Malt', 'GL')

zip_file = os.path.join(current_dir, 'glslang.zip')

glslang_url = {
'Windows' : "https://github.com/KhronosGroup/glslang/releases/download/master-tot/glslang-master-windows-x64-Release.zip",
'Linux' : "https://github.com/KhronosGroup/glslang/releases/download/master-tot/glslang-master-linux-Release.zip",
'Darwin' : "https://github.com/KhronosGroup/glslang/releases/download/master-tot/glslang-master-osx-Release.zip",
}
glslang_url = glslang_url[platform.system()]

zipped_path = 'bin/glslangValidator'
target_path = os.path.join(gl_folder, '.glslang')
if platform.system() == 'Windows':
    zipped_path += '.exe'
    target_path += '.exe'

import urllib.request
urllib.request.urlretrieve(glslang_url, zip_file)

with zipfile.ZipFile(zip_file) as z:
    with z.open(zipped_path) as zip, open(target_path, 'wb') as unzip:
        shutil.copyfileobj(zip, unzip)

# Set as executable (Needed on Linux)
os.chmod(target_path, os.stat(target_path).st_mode | stat.S_IEXEC)

os.remove(zip_file)
