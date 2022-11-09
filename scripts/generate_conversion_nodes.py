result = ''

base_types = ('float','int','uint','bool')
vector_types = ('vec','ivec','uvec','bvec')

for to_base_type in base_types:
    result += f'//{to_base_type}\n'
    for from_base_type in base_types:
        if from_base_type == to_base_type:
            continue
        result += '/* META @meta: internal=true; */\n'
        param = from_base_type[:1]
        result += f'{to_base_type} {to_base_type}_from_{from_base_type}({from_base_type} {param}) {{ return {to_base_type}({param}); }}\n'
    
    result += '\n'

for to_vector_type in vector_types:
    for to_vector_len in range(2,5):
        to_vector = f'{to_vector_type}{to_vector_len}'
        
        result += f'//{to_vector}\n'
        
        for base_type in base_types:
            result += '/* META @meta: internal=true; */\n'
            param = base_type[:1]
            conversion = f'{to_vector}({param})'
            if to_vector_len == 4 and to_vector_type != 'bvec':
                conversion = f'{to_vector}({param}, {param}, {param}, 1)'
            result += f'{to_vector} {to_vector}_from_{base_type}({base_type} {param}) {{ return {conversion}; }}\n'

        for from_vector_type in vector_types:
            for from_vector_len in range(2,5):
                if from_vector_type == to_vector_type and from_vector_len == to_vector_len:
                    continue
                from_vector = f'{from_vector_type}{from_vector_len}'

                param = 'v'
                if to_vector_len < from_vector_len:
                    param += '.xyzw'[:to_vector_len+1]
                if to_vector_len > from_vector_len:
                    for i in range(from_vector_len, to_vector_len):
                        if to_vector_type != 'bvec' and to_vector_len == 4 and i == to_vector_len - 1:
                            param += ', 1'
                        else:
                            param += ', 0'
                conversion = f'{to_vector}({param})'

                result += '/* META @meta: internal=true; */\n'
                result += f'{to_vector} {to_vector}_from_{from_vector}({from_vector} v) {{ return {conversion}; }}\n'
        
        result += '\n'


print(result)
