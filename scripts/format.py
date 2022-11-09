def scan_dirs(path, file_callback):
    import os
    for e in os.scandir(path):
        if e.is_file():
            extension = e.name.split('.')[-1]
            if extension in ('py','glsl','h','c','cpp'):
                file_callback(e)
        if e.is_dir():
            if e.name.startswith('.') or e.name.startswith('__'):
                continue
            scan_dirs(e, file_callback)


def fix_whitespace(path):
    with open(path, 'r+') as f:
        result = ''
        lines = f.readlines()
        for i, line in enumerate(lines):
            new_line = ''
            if line.isspace():
                while i < len(lines) - 1:
                    i += 1
                    found_next_line = False
                    if lines[i].isspace() == False:
                        for c in lines[i]:
                            if c.isspace():
                                new_line += c
                            else:
                                break
                        found_next_line = True
                    else:
                        continue
                    if found_next_line:
                        break
            else:
                new_line = line.rstrip()
            result += new_line
            result += '\n'
        result = result.splitlines(keepends=True)
        while len(result) > 1 and result[-1].isspace():
            while result[-1].isspace():
                result.pop()
        result = ''.join(result)
        f.seek(0)
        f.truncate()
        f.write(result)


import sys

scan_dirs(sys.argv[1], fix_whitespace)
