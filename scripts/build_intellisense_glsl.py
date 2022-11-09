import os, json, xmltodict, traceback, copy

SKIP_TERMS = ['image','atomic','barrier','memory','shadow','noise']

DEFINES = ['in','out','inout','uniform','varying','layout(index)','discard','uint unsigned int','atomic_uint uint']

DEFINES = ''.join(['#define ' + define + '\n' for define in DEFINES])

GENERICS = {
    'genType': ['float',  'vec2',  'vec3',  'vec4'],
    'genDType':['double', 'dvec2', 'dvec3', 'dvec4'],
    'genIType':['int',    'ivec2', 'ivec3', 'ivec4'],
    'genUType':['uint',   'uvec2', 'uvec3', 'uvec4'],
    'genBType':['bool',   'bvec2', 'bvec3', 'bvec4'],
}

#Start with types we don't want to define
BUILTINS = [*GENERICS.keys(),'gvec4']

TYPES = ''

FUNCTIONS = ''

def add_type(type_name):
    global TYPES
    TYPES += 'struct ' + type_name + ' {};\n'

def add_generic_type(type_name):
    if type_name.startswith('g') and type_name not in BUILTINS:
        BUILTINS.append(type_name)
        for replace in ['','i','u']:
            add_type(replace + type_name[1:])

for generic in GENERICS.values():
    for _type in generic[1:]:
        add_type(_type)

for mat_type in ['mat2','mat3','mat4','mat2x2','mat2x3','mat2x4','mat3x2','mat3x3','mat3x4','mat4x2','mat4x3','mat4x4']:
    add_type(mat_type)
    add_type('d'+mat_type)

def output_function(signatures, docstring):
    generic_types = []
    has_optional = False
    for _type, name in signatures:
        for term in SKIP_TERMS:
            if term in _type.lower() or term in name.lower():
                return
        if _type.startswith('['):
            has_optional = True
        _type = _type.split(' ')[-1]
        if _type.startswith('g') or _type.endswith('vec') or _type.endswith('mat'):
            if _type not in generic_types:
                generic_types.append(_type)
    resolve_generics(signatures, generic_types, has_optional, docstring)

def resolve_generics(signatures, generic_types, has_optional, docstring):
    if has_optional:
        for remove in [True, False]:
            _signatures = copy.deepcopy(signatures)
            if remove:
                _signatures.pop()
            else:
                _signatures[-1][0]= _signatures[-1][0].replace('[','').replace(']','')
                _signatures[-1][1]= _signatures[-1][1].replace('[','').replace(']','')
            resolve_generics(_signatures, copy.deepcopy(generic_types), False, docstring)
    else:
        string = '//' + docstring + '\n'
        if len(generic_types) > 0:
            string += 'template<'
            while len(generic_types) > 0:
                _type = generic_types.pop(0)
                add_generic_type(_type)
                string += 'typename '+_type
                if len(generic_types) > 0:
                    string += ', '
            string += '> '

        func = signatures.pop(0)
        string += func[0] + ' ' + func[1] + '('
        while len(signatures) > 0:
            param = signatures.pop(0)
            string += param[0] + ' ' + param[1]
            if len(signatures) > 0:
                string += ', '
        string += ');'
        global FUNCTIONS
        FUNCTIONS += string + '\n'
        #print(string)

for entry in os.listdir('gl4'):
    if entry.endswith('.xml'):
        with open(os.path.join('gl4', entry), 'r') as xml:
            xml = xml.read()
            try:
                d = xmltodict.parse(xml)
                if d['refentry']['refsynopsisdiv']['title'] == 'Declaration':
                    try:
                        print(entry,'---------------------------------------------------------')
                        docstring = d['refentry']['refnamediv']['refpurpose']
                        synops = d['refentry']['refsynopsisdiv']['funcsynopsis']
                        if isinstance(synops, list) == False:
                            synops = [synops]
                        for synop in synops:
                            functions = synop['funcprototype']
                            if isinstance(functions, list) == False:
                                functions = [functions]
                            for function in functions:
                                name = function['funcdef']['function']
                                return_type = function['funcdef']['#text']
                                signatures = [[return_type, name]]
                                declaration = return_type + ' ' + name + '('
                                parameters = function['paramdef']
                                if isinstance(parameters, str) == False: #not void
                                    if isinstance(parameters, list) == False:
                                        parameters = [parameters]
                                    for parameter in parameters:
                                        param_type = parameter['#text']
                                        param_name = parameter['parameter']
                                        signatures.append([param_type, param_name])
                                        declaration += param_type + ' ' + param_name + ', '
                                if declaration.endswith(', '):
                                    declaration = declaration[:-2]
                                declaration += ');'
                                print(signatures)
                                output_function(signatures, docstring)
                    except Exception as e:
                        print('exception')
                        #print(json.dumps(d['refentry']['refsynopsisdiv'], indent=4))
                        print(traceback.format_exc())
            except Exception as e:
                #print('FAILED', entry)
                pass

SHORTEN = True
if SHORTEN:
    FUNCTIONS = FUNCTIONS.replace('genType', 'T')
    FUNCTIONS = FUNCTIONS.replace('genDType', 'D')
    FUNCTIONS = FUNCTIONS.replace('genIType', 'I')
    FUNCTIONS = FUNCTIONS.replace('genUType', 'U')
    FUNCTIONS = FUNCTIONS.replace('genBType', 'B')

FINAL_FILE = f'''
//This file contains a series of C++ macros, structs and function declarations
//to make GLSL autocompletion work with C++ autocompletion implementations

#ifdef __INTELLISENSE__

//Define GLSL keywords

{DEFINES}

//Declare GLSL built-in types

{TYPES}

//Declare GLSL standard library functions

{FUNCTIONS}

#endif
'''

with open('intellisense.glsl', 'w') as f:
    f.write(FINAL_FILE)
