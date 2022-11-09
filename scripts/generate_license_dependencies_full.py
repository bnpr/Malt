import os

TOP_DIR = os.path.join(os.path.dirname(__file__), os.pardir)

dependencies = open(os.path.join(TOP_DIR, 'LICENSE - DEPENDENCIES')).read()

result = ''

for dependency in dependencies.split('\n\n'):
    lines = dependency.splitlines()
    for i, line in enumerate(lines):
        if i < 3:
            result += line
        else:
            url = line.replace('github.com', 'raw.githubusercontent.com').replace('blob/','')
            from urllib.request import urlopen
            content = urlopen(url).read().decode('utf-8')
            result+=content
        result+='\n'
    result += '*'*80
    result+='\n'

open(os.path.join(TOP_DIR, 'LICENSE - DEPENDENCIES (FULL TEXT)'), 'w').write(result)
