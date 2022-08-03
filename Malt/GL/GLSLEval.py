def glsl_vector(length, *args):
    unpacked_args = []
    for arg in args:
        try:
            unpacked_args.extend([*arg])
        except:
            unpacked_args.append(arg)
    unpacked_args = [float(arg) for arg in unpacked_args]
    if len(unpacked_args) == 0:
        return (0.0)*length
    elif len(unpacked_args) == 1:
        return (unpacked_args[0],) * length
    else:
        assert(len(unpacked_args) == length)
        return tuple(unpacked_args)

def vec2(*args):
    return glsl_vector(2, *args)

def vec3(*args):
    return glsl_vector(3, *args)

def vec4(*args):
    return glsl_vector(4, *args)

ivec2 = vec2
ivec3 = vec3
ivec4 = vec4

uvec2 = vec2
uvec3 = vec3
uvec4 = vec4

def glsl_eval(str):
    true = True
    false = False
    return eval(str)

