def glsl_vector(convert, length, *args):
    unpacked_args = []
    for arg in args:
        try:
            unpacked_args.extend([*arg])
        except:
            unpacked_args.append(arg)
    unpacked_args = [convert(arg) for arg in unpacked_args]
    if len(unpacked_args) == 0:
        return (0.0)*length
    elif len(unpacked_args) == 1:
        return (unpacked_args[0],) * length
    else:
        assert(len(unpacked_args) == length)
        return tuple(unpacked_args)

def _vec2(convert, *args): return glsl_vector(convert, 2, *args)
def _vec3(convert, *args): return glsl_vector(convert, 3, *args)
def _vec4(convert, *args): return glsl_vector(convert, 4, *args)

def vec2(*args): return _vec2(float, *args)
def vec3(*args): return _vec3(float, *args)
def vec4(*args): return _vec4(float, *args)

def ivec2(*args): return _vec2(int, *args)
def ivec3(*args): return _vec3(int, *args)
def ivec4(*args): return _vec4(int, *args)

def uint(n): return max(int(n), 0)

def uvec2(*args): return _vec2(uint, *args)
def uvec3(*args): return _vec3(uint, *args)
def uvec4(*args): return _vec4(uint, *args)

def glsl_eval(str):
    true = True
    false = False
    return eval(str)

