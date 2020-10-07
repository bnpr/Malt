import urllib.request, shutil, os, platform, zipfile, tarfile, subprocess

dependencies = ['PyOpenGL','pcpp', 'Pyrr']

version = '2.90'
full_version = '2.90.1'

os_name = 'windows64'
file_format = 'zip'

if platform.system() == 'Linux':
    os_name = 'linux64'
    file_format = 'tar.xz'

url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender{}/blender-{}-{}.{}".format(version, full_version, os_name, file_format)
file_name = "blender.{}".format(file_format)

blender_folder = "blender-{}-{}".format(full_version, os_name)

python_folder = os.path.join('.', blender_folder, version, 'python')
python_path = os.path.join(python_folder, 'bin', 'python')
if platform.system() == 'Linux':
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

subprocess.check_call([python_path, '-m', 'ensurepip'])
for dependency in dependencies:
    subprocess.check_call([python_path, '-m', 'pip', 'install', dependency, '--target', site_packages])

blender_malt_folder = os.path.join('..', '..', 'BlenderMalt')
addons_folder = os.path.join(blender_folder, version, 'scripts', 'addons', 'BlenderMalt')

from distutils.dir_util import copy_tree
copy_tree(blender_malt_folder, addons_folder)

print("::set-env name=_BLENDER_DIR::{}".format(blender_folder))
