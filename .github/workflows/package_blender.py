import urllib.request, shutil, os, platform, zipfile, tarfile, subprocess, shutil
from distutils.dir_util import copy_tree

blender_malt_folder = os.path.join('..', '..', 'BlenderMalt')

CBlenderMalt_folder = os.path.join(blender_malt_folder, 'CBlenderMalt')
subprocess.check_call(['python', 'build.py'], cwd=CBlenderMalt_folder)

dependencies = ['PyOpenGL','pcpp', 'Pyrr']

version = '2.90'
full_version = '2.90.1'

os_name = 'windows64'
file_format = 'zip'

if platform.system() == 'Linux':
    os_name = 'linux64'
    file_format = 'tar.xz'

if platform.system() == 'Darwin':
    os_name = 'macOS'
    file_format = 'dmg'

url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender{}/blender-{}-{}.{}".format(version, full_version, os_name, file_format)
file_name = "blender.{}".format(file_format)

blender_folder = "blender-{}-{}".format(full_version, os_name)
blender_content_folder = blender_folder

if platform.system() == 'Darwin':
    blender_content_folder = os.path.join(blender_folder, 'Blender.app', 'Contents', 'Resources')

python_folder = os.path.join(blender_content_folder, version, 'python')
python_path = os.path.join(python_folder, 'bin', 'python')

if platform.system() != 'Windows':
    python_path = python_path + '3.7m'
site_packages = os.path.join(python_folder, 'lib', 'site-packages')

with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)

if file_format == 'zip':
    with zipfile.ZipFile(file_name, 'r') as file:
        file.extractall('.')
elif file_format == 'tar.xz':
    with tarfile.open(file_name, 'r') as file:
        file.extractall('.')
elif file_format == 'dmg':
    subprocess.check_call(['hdiutil', 'attach', file_name])
    mounted_blender = os.path.join('/Volumes', 'Blender', 'Blender.app')
    copy_tree(mounted_blender, os.path.join(blender_folder, 'Blender.app'))

subprocess.check_call([python_path, '-m', 'ensurepip'])
for dependency in dependencies:
    subprocess.check_call([python_path, '-m', 'pip', 'install', dependency, '--target', site_packages])

addons_folder = os.path.join(blender_content_folder, version, 'scripts', 'addons', 'BlenderMalt')

copy_tree(blender_malt_folder, addons_folder)

shutil.make_archive(blender_folder, 'zip', '.', blender_folder)

print("::set-env name=_BLENDER_FILE::{}.zip".format(blender_folder))
