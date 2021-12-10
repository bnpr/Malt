# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import os, time
from itertools import chain
from Malt.Parameter import Parameter, Type
import bpy
from BlenderMalt import malt_path_getter, malt_path_setter
from . MaltProperties import MaltPropertyGroup
from . import MaltPipeline


def get_pipeline_graph(context):
    if context is None or context.space_data is None or context.space_data.edit_tree is None:
        return None
    return context.space_data.edit_tree.get_pipeline_graph()

class MaltTree(bpy.types.NodeTree):

    bl_label = "Malt Node Tree"
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'MALT'
    
    def poll_material(self, material):
        return material.malt.shader_nodes is self
    
    graph_type: bpy.props.StringProperty(name='Type')

    library_source : bpy.props.StringProperty(name="Shader Library", subtype='FILE_PATH',
        set=malt_path_setter('library_source'), get=malt_path_getter('library_source'))

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False)

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup)

    def get_source_language(self):
        return self.get_pipeline_graph().language

    def get_transpiler(self):
        if self.get_source_language() == 'GLSL':
            return GLSLTranspiler
        elif self.get_source_language() == 'Python':
            return PythonTranspiler

    def get_library_path(self):
        if self.library_source != '':
            src_path = bpy.path.abspath(self.library_source, library=self.library)
            if os.path.exists(src_path):
                return src_path
        return None
    
    def get_library(self):
        library_path = self.get_library_path()
        if library_path:
            return get_libraries()[library_path]
        else:
            return get_empty_library()
    
    def get_full_library(self):
        #TODO: Cache
        result = get_empty_library()
        result['functions'].update(self.get_pipeline_graph().functions)
        result['structs'].update(self.get_pipeline_graph().structs)
        result['functions'].update(self.get_library()['functions'])
        result['structs'].update(self.get_library()['structs'])
        return result
    
    def get_pipeline_graph(self):
        bridge = MaltPipeline.get_bridge()
        if bridge and self.graph_type in bridge.graphs:
            return bridge.graphs[self.graph_type]
        return None
    
    def cast(self, from_type, to_type):
        cast_function = f'{to_type}_from_{from_type}'
        lib = self.get_full_library()
        if cast_function in lib['functions']:
            #TODO: If more than 1 parameter, check if they have default values
            if len(lib['functions'][cast_function]['parameters']) == 1:
                return cast_function
        return None
    
    def get_struct_type(self, struct_type):
        lib = self.get_full_library()
        if struct_type in lib['structs']:
            return lib['structs'][struct_type]
        return None
    
    def get_generated_source_dir(self):
        import os, tempfile
        base_path = tempfile.gettempdir()
        if bpy.context.blend_data.is_saved or self.library:
            base_path = bpy.path.abspath('//', library=self.library)
        return os.path.join(base_path,'malt-shaders')

    def get_generated_source_path(self):
        import os
        file_prefix = 'temp'
        if self.library:
            file_prefix = bpy.path.basename(self.library.filepath).split('.')[0]
        elif bpy.context.blend_data.is_saved:  
            file_prefix = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            return os.path.join(self.get_generated_source_dir(),'{}-{}{}'.format(file_prefix, self.name, pipeline_graph.file_extension))
        return None
    
    def get_generated_source(self):
        output_nodes = []
        linked_nodes = []
        
        pipeline_graph = self.get_pipeline_graph()
        if pipeline_graph:
            for node in self.nodes:
                if isinstance(node, MaltIONode) and node.is_output:
                    output_nodes.append(node)
                    linked_nodes.append(node)
        
        def add_node_inputs(node, list):
            for input in node.inputs:
                if input.is_linked:
                    new_node = input.links[0].from_node
                    if new_node not in list:
                        add_node_inputs(new_node, list)
                        list.append(new_node)
                    if new_node not in linked_nodes:
                        linked_nodes.append(new_node)
        
        transpiler = self.get_transpiler()
        def get_source(output):
            nodes = []
            add_node_inputs(output, nodes)
            code = ''
            for node in nodes:
                if isinstance(node, MaltNode):
                    code += node.get_source_code(transpiler) + '\n'
            code += output.get_source_code(transpiler)
            return code

        shader ={}
        for output in output_nodes:
            shader[output.io_type] = get_source(output)
        shader['GLOBAL'] = ''
        library_path = self.get_library_path()
        if library_path:
            shader['GLOBAL'] += '#include "{}"\n'.format(library_path)
        for node in linked_nodes:
            if isinstance(node, MaltNode):
                shader['GLOBAL'] += node.get_source_global_parameters(transpiler)
        return pipeline_graph.generate_source(shader)
    
    def reload_nodes(self):
        self.disable_updates = True
        try:
            for node in self.nodes:
                if isinstance(node, MaltNode):
                    node.setup()
            for node in self.nodes:
                if isinstance(node, MaltNode):
                    node.update()
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False

    def update(self):
        if self.disable_updates:
            return

        if self.get_pipeline_graph() is None:
            return

        self.disable_updates = True
        try:
            for link in self.links:
                try:
                    if (link.from_socket.array_size != link.to_socket.array_size or 
                        (link.from_socket.data_type != link.to_socket.data_type and
                        self.cast(link.from_socket.data_type, link.to_socket.data_type) is None)):
                        self.links.remove(link)
                except:
                    pass
            
            source = self.get_generated_source()
            source_dir = self.get_generated_source_dir()
            source_path = self.get_generated_source_path()
            import pathlib
            pathlib.Path(source_dir).mkdir(parents=True, exist_ok=True)
            with open(source_path,'w') as f:
                f.write(source)
            from BlenderMalt import MaltMaterial
            MaltMaterial.track_shader_changes()
        except:
            import traceback
            traceback.print_exc()
        self.disable_updates = False
        
        # Force a depsgraph update. 
        # Otherwise these will be outddated in scene_eval
        self.update_tag()

def setup_node_trees():
    graphs = MaltPipeline.get_bridge().graphs
    for name, graph in graphs.items():
        preload_menus(graph.structs, graph.functions)
    
    track_library_changes(force_update=True, disable_tree_updates=True)
    
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'MaltTree':
            tree.reload_nodes()
            tree.update()

__LIBRARIES = {}    
def get_libraries():
    return __LIBRARIES
def get_empty_library():
    return {
        'structs':{},
        'functions':{},
        'paths':[],
    }
__TIMESTAMP = time.time()

def track_library_changes(force_update=False, disable_tree_updates=False):
    if bpy.context.scene.render.engine != 'MALT' and force_update == False:
        return 1

    global __LIBRARIES
    global __TIMESTAMP
    start_time = time.time()

    #purge unused libraries
    new_dic = {}
    for tree in bpy.data.node_groups:
        if isinstance(tree, MaltTree):
            src_path = tree.get_library_path()
            if src_path:
                if src_path in __LIBRARIES:
                    new_dic[src_path] = __LIBRARIES[src_path]
                else:
                    new_dic[src_path] = None
    __LIBRARIES = new_dic

    needs_update = set()
    for path, library in __LIBRARIES.items():
        root_dir = os.path.dirname(path)
        if os.path.exists(path):
            if library is None:
                needs_update.add(path)
            else:
                for sub_path in library['paths']:
                    sub_path = os.path.join(root_dir, sub_path)
                    if os.path.exists(sub_path):
                        # Don't track individual files granularly since macros can completely change them
                        if os.stat(sub_path).st_mtime > __TIMESTAMP:
                            needs_update.add(path)
                            break
    
    if len(needs_update) > 0:
        results = MaltPipeline.get_bridge().reflect_source_libraries(needs_update)
        for path, reflection in results.items():
            __LIBRARIES[path] = reflection
            preload_menus(reflection['structs'], reflection['functions'])
        
        if disable_tree_updates == False:
            for tree in bpy.data.node_groups:
                if isinstance(tree, MaltTree):
                    src_path = tree.get_library_path()
                    if src_path and src_path in needs_update:
                        tree.update()
    
    __TIMESTAMP = start_time
    return 0.1


__TYPE_COLORS = {}
def get_type_color(type):
    if type not in __TYPE_COLORS:
        import random, hashlib
        seed = hashlib.sha1(type.encode('ascii')).digest()
        rand = random.Random(seed)
        __TYPE_COLORS[type] = (rand.random(),rand.random(),rand.random(),1.0)
    return __TYPE_COLORS[type]

#TODO: Send transpiler along graph types
class SourceTranspiler():
    
    @classmethod
    def asignment(self, name, asignment):
        pass

    @classmethod
    def declaration(self, type, size, name, initialization=None):
        pass

    @classmethod
    def global_reference(self, node_name, parameter_name):
        pass
    
    @classmethod
    def global_declaration(self, type, size, name, initialization=None):
        pass

    @classmethod
    def parameter_reference(self, node_name, parameter_name):
        pass

    @classmethod
    def io_parameter_reference(self, parameter_name, io_type):
        return parameter_name

    @classmethod
    def is_instantiable_type(self, type):
        return True

    @classmethod
    def call(self, name, parameters=[], full_statement=False):
        pass

    @classmethod
    def result(self, result):
        pass

    @classmethod
    def scoped(self, code):
        pass

class GLSLTranspiler(SourceTranspiler):

    @classmethod
    def asignment(self, name, asignment):
        return f'{name} = {asignment};\n'

    @classmethod
    def declaration(self, type, size, name, initialization=None):
        array = '' if size == 0 else f'[{size}]'
        asignment = f' = {initialization}' if initialization else ''
        return f'{type} {name}{array}{asignment};\n'

    @classmethod    
    def global_reference(self, node_name, parameter_name):
        return f'U_0{node_name}_0_{parameter_name}'

    @classmethod
    def global_declaration(self, type, size, name, initialization=None):
        return 'uniform ' + self.declaration(type, size, name, initialization)

    @classmethod
    def parameter_reference(self, node_name, parameter_name):
        return f'{node_name}_0_{parameter_name}'

    @classmethod    
    def is_instantiable_type(self, type):
        return type.startswith('sampler') == False

    @classmethod
    def call(self, function, name, parameters=[], post_parameter_initialization = ''):
        src = ''
        for i, parameter in enumerate(function['parameters']):
            if parameter['io'] in ['out','inout']:
                initialization = parameters[i]
                src_reference = self.parameter_reference(name, parameter['name'])
                src += self.declaration(parameter['type'], parameter['size'], src_reference, initialization)
                parameters[i] = src_reference
        src += post_parameter_initialization

        initialization = f'{function["name"]}({",".join(parameters)})'
        
        if function['type'] != 'void' and self.is_instantiable_type(function['type']):
            src += self.declaration(function['type'], 0, self.parameter_reference(name, 'result'), initialization)
        else:
            src += initialization + ';\n'
        
        return src

    @classmethod
    def result(self, result):
        return f'return {result};\n'

    @classmethod    
    def scoped(self, code):
        import textwrap
        code = textwrap.indent(code, '\t')
        return f'{{\n{code}}}\n'

class PythonTranspiler(SourceTranspiler):

    @classmethod
    def asignment(self, name, asignment):
        return f'{name} = {asignment}\n'

    @classmethod
    def declaration(self, type, size, name, initialization=None):
        if initialization is None: initialization = 'None'
        return self.asignment(name, initialization)

    @classmethod    
    def global_reference(self, node_name, parameter_name):
        return f'PARAMETERS["{node_name}"]["{parameter_name}"]'

    @classmethod    
    def global_declaration(self, type, size, name, initialization=None):
        return ''
        return self.declaration(type, size, name, initialization)

    @classmethod    
    def parameter_reference(self, node_name, parameter_name):
        return f'{node_name}_parameters["{parameter_name}"]'

    @classmethod    
    def io_parameter_reference(self, parameter_name, io_type):
        if io_type == 'out':
            return f'OUT["{parameter_name}"]'
        else:
            return f'IN["{parameter_name}"]'

    @classmethod
    def call(self, function, name, parameters=[], post_parameter_initialization = ''):
        src = ''
        src += f'{name}_parameters = {{}}\n'
        for i, parameter in enumerate(function['parameters']):
            initialization = parameters[i]
            if initialization is None:
                initialization = 'None'
            parameter_reference = self.parameter_reference(name, parameter['name'])
            src += f'{parameter_reference} = {initialization}\n'
        src += post_parameter_initialization
        src += f'run_node("{name}", "{function["name"]}", {name}_parameters)\n'
        return src

    @classmethod
    def result(self, result):
        return f'return {result}\n'

    @classmethod    
    def scoped(self, code):
        import textwrap
        code = textwrap.indent(code, '\t')
        return f'if True:\n{code}'
        

class MaltSocket(bpy.types.NodeSocket):
    
    bl_label = "Malt Node Socket"

    def on_type_update(self, context):
        self.node.on_socket_update(self)

    data_type: bpy.props.StringProperty(update=on_type_update)

    array_size: bpy.props.IntProperty(default=0, update=on_type_update)
    
    default_initialization: bpy.props.StringProperty(default='')
    
    show_in_material_panel: bpy.props.BoolProperty(default=True)

    def is_instantiable_type(self):
        return self.data_type.startswith('sampler') == False

    def get_source_reference(self, target_type=None):
        if not self.is_instantiable_type() and not self.is_output and self.get_linked() is not None:
            self.get_linked().get_source_reference()
        else:
            reference = self.node.get_source_socket_reference(self)
            if target_type and target_type != self.data_type:
                cast_function = self.node.id_data.cast(self.data_type, target_type)
                return f'{cast_function}({reference})'
            return reference
    
    def get_source_global_reference(self):
        return self.id_data.get_transpiler().global_reference(self.node.get_source_name(), self.name)
    
    def is_struct_member(self):
        return '.' in self.name
    
    def get_struct_socket(self):
        if self.is_struct_member():
            struct_socket_name = self.name.split('.')[0]
            if self.is_output:
                return self.node.outputs[struct_socket_name]
            else:
                return self.node.inputs[struct_socket_name]
        return None
    
    def get_source_initialization(self):
        if self.is_linked:
            return self.get_linked().get_source_reference(self.data_type)
        elif self.default_initialization != '':
            return self.default_initialization
        elif self.is_struct_member() and (self.get_struct_socket().is_linked or self.get_struct_socket().default_initialization != ''):
            return None
        else:
            return self.get_source_global_reference()

    def get_linked(self):
        def get_linked_internal(socket):
            if len(socket.links) == 0:
                return None
            else:
                link = socket.links[0]
                linked = link.to_socket if socket.is_output else link.from_socket
                if isinstance(linked.node, bpy.types.NodeReroute):
                    sockets = linked.node.inputs if linked.is_output else linked.node.outputs
                    if len(sockets) == 0:
                        return None
                    return get_linked_internal(sockets[0])
                else:
                    return linked
        return get_linked_internal(self)
    
    def get_ui_label(self):
        type = self.data_type
        if self.array_size > 0:
            type += f'[{self.array_size}]'
        if self.is_output:
            return f'({type}) : {self.name}'
        else:
            return f'{self.name} : ({type})'
    
    def draw(self, context, layout, node, text):
        if context.region.type != 'UI' or self.get_source_global_reference() == self.get_source_initialization():
            text = self.get_ui_label()
            node.draw_socket(context, layout, self, text)
            if context.region.type == 'UI':
                icon = 'HIDE_OFF' if self.show_in_material_panel else 'HIDE_ON'
                layout.prop(self, 'show_in_material_panel', text='', icon=icon)
    
    def setup_shape(self):
        from Malt.Parameter import Parameter
        base_type = True
        try:
            Parameter.from_glsl_type(self.data_type)
        except:
            base_type = False
        array_type = self.array_size > 0
        if base_type:
            if array_type:
                self.display_shape = 'CIRCLE_DOT'
            else:
                self.display_shape = 'CIRCLE'
        else:
            if array_type:
                self.display_shape = 'SQUARE_DOT'
            else:
                self.display_shape = 'SQUARE'

    def draw_color(self, context, node):
        return get_type_color(self.data_type)
    

class MaltNode():

    malt_parameters : bpy.props.PointerProperty(type=MaltPropertyGroup)

    disable_updates : bpy.props.BoolProperty(name="Disable Updates", default=False)
    
    first_setup : bpy.props.BoolProperty(default=True)

    # Blender will trigger update callbacks even before init and update has finished
    # So we use some wrappers to get a more sane behaviour

    def _disable_updates_wrapper(self, function):
        tree = self.id_data
        tree.disable_updates = True
        self.disable_updates = True
        try:
            function()
        except:
            import traceback
            traceback.print_exc()
        tree.disable_updates = False
        self.disable_updates = False

    def init(self, context):
        self._disable_updates_wrapper(self.malt_init)
        
    def setup(self, context=None):
        self._disable_updates_wrapper(self.malt_setup)
        self.first_setup = False

    def update(self):
        if self.disable_updates:
            return
        self._disable_updates_wrapper(self.malt_update)
        
    def malt_init(self):
        pass

    def malt_setup(self):
        pass
    
    def malt_update(self):
        pass

    def on_socket_update(self, socket):
        pass

    def setup_sockets(self, inputs, outputs, expand_structs=True):
        from Malt.Parameter import Parameter, Type
        def _expand_structs(sockets):
            result = {}
            for name, dic in sockets.items():
                result[name] = dic
                struct_type = self.id_data.get_struct_type(dic['type'])
                if struct_type:
                    for member in struct_type['members']:
                        result[f"{name}.{member['name']}"] = member
            return result
        if expand_structs:
            inputs = _expand_structs(inputs)
            outputs = _expand_structs(outputs)
        def setup(current, new):
            remove = []
            for e in current.keys():
                if e not in new:
                    #TODO: deactivate linked, don't delete them?
                    remove.append(current[e])
            for e in remove:
                current.remove(e)
            for name, dic in new.items():
                type = dic['type']
                size = dic['size'] if 'size' in dic else 0
                if name not in current:
                    current.new('MaltSocket', name)
                if isinstance(type, Parameter):
                    current[name].data_type = type.type_string()
                    current[name].array_size = 0 #TODO
                else:
                    current[name].data_type = type
                    current[name].array_size = size
                try:
                    current[name].default_initialization = dic['meta']['init']
                except:
                    current[name].default_initialization = ''
        setup(self.inputs, inputs)
        setup(self.outputs, outputs)
        parameters = {}
        for name, input in self.inputs.items():
            parameter = None
            if name in inputs.keys() and isinstance(inputs[name]['type'], Parameter):
                parameter = inputs[name]['type']
            elif input.array_size == 0:
                try:
                    parameter = Parameter.from_glsl_type(input.data_type)
                    parameter.default_value = eval(inputs[name]['meta']['value'])
                except:
                    pass
            if parameter:
                parameters[input.name] = parameter
        self.malt_parameters.setup(parameters, skip_private=False)
        self.setup_socket_shapes()
        if self.first_setup:
            self.setup_width()
    
    def setup_width(self):
        max_len = len(self.name)
        for input in self.inputs.values():
            max_len = max(max_len, len(input.get_ui_label()))
        for output in self.outputs.values():
            max_len = max(max_len, len(output.get_ui_label()))
        #TODO: Measure actual string width
        self.width = max(self.width, max_len * 10)

    def get_source_name(self):
        name = self.name.replace('.','_')
        name = '_' + ''.join(char for char in name if char.isalnum() or char == '_')
        return name.replace('__','_')

    def get_source_code(self, transpiler):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(self)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(self)

    def get_source_socket_reference(self, socket):
        if self.id_data.get_source_language() == 'GLSL':
            return '/*{} not implemented*/'.format(socket.name)
        elif self.id_data.get_source_language() == 'Python':
            return '# {} not implemented'.format(socket.name)
    
    def sockets_to_global_parameters(self, sockets, transpiler):
        code = ''
        for socket in sockets:
            if socket.data_type != '' and socket.get_linked() is None and socket.is_struct_member() == False:
                code += transpiler.global_declaration(socket.data_type, socket.array_size, socket.get_source_global_reference())
        return code
    
    def get_source_global_parameters(self, transpiler):
        return self.sockets_to_global_parameters(self.inputs, transpiler)
    
    def setup_socket_shapes(self):
        for socket in chain(self.inputs.values(), self.outputs.values()):
            socket.setup_shape()
    
    def draw_socket(self, context, layout, socket, text):
        layout.label(text=text)
        if socket.is_output == False and socket.is_linked == False and socket.default_initialization == '':
            if socket.is_struct_member() and (socket.get_struct_socket().is_linked or socket.get_struct_socket().default_initialization != ''):
                return
            self.malt_parameters.draw_parameter(layout, socket.name, None, is_node_socket=True)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MaltTree'
    
    def draw_label(self):
        return self.name


class MaltStructNode(bpy.types.Node, MaltNode):
    
    bl_label = "Struct Node"

    def malt_setup(self, context=None):
        if self.first_setup:
            self.name = self.struct_type

        inputs = {}
        inputs[self.struct_type] = {'type' : self.struct_type}
        outputs = {}
        outputs[self.struct_type] = {'type' : self.struct_type}

        self.setup_sockets(inputs, outputs)

    struct_type : bpy.props.StringProperty(update=MaltNode.setup)

    def get_struct(self):
        graph = self.id_data.get_pipeline_graph()
        if self.struct_type in graph.structs:
            return graph.structs[self.struct_type]
        else:
            return self.id_data.get_library()['structs'][self.struct_type]

    def get_source_socket_reference(self, socket):
        if socket.name == self.struct_type:
            return self.get_source_name()
        else:
            return socket.name.replace(self.struct_type, self.get_source_name())
    
    def struct_input_is_linked(self):
        return self.inputs[self.struct_type].get_linked() is not None

    def get_source_code(self, transpiler):
        code = ''
        
        for input in self.inputs:
            initialization = input.get_source_initialization()
            if input.is_struct_member():
                if initialization:
                    code += transpiler.asignment(input.get_source_reference(), initialization)
            else:
                code += transpiler.declaration(input.data_type, 0, self.get_source_name(), initialization)
        
        return code
    

class MaltFunctionNode(bpy.types.Node, MaltNode):
    
    bl_label = "Function Node"
    
    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = function['name']

        inputs = {}
        outputs = {}

        if function['type'] != 'void':
            outputs['result'] = {'type': function['type']} #TODO: Array return type
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout']:
                outputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout']:
                inputs[parameter['name']] = parameter
        
        self.setup_sockets(inputs, outputs)

    function_type : bpy.props.StringProperty(update=MaltNode.setup)

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        if self.function_type in graph.functions:
            return graph.functions[self.function_type]
        else:
            return self.id_data.get_library()['functions'][self.function_type]

    def get_source_socket_reference(self, socket):
        transpiler = self.id_data.get_transpiler()
        if transpiler.is_instantiable_type(socket.data_type):
            return transpiler.parameter_reference(self.get_source_name(), socket.name)
        else:
            source = self.get_source_code(transpiler)
            return source.splitlines()[-1].split('=')[-1].split(';')[0]

    def get_source_code(self, transpiler):
        function = self.get_function()
        source_name = self.get_source_name()

        post_parameter_initialization = ''
        for input in self.inputs:
            if input.is_struct_member():
                initialization = input.get_source_initialization()
                if initialization:
                    post_parameter_initialization += transpiler.asignment(input.get_source_reference(), initialization)

        parameters = []
        for parameter in function['parameters']:
            initialization = None
            if parameter['io'] in ['','in','inout']:
                socket = self.inputs[parameter['name']]
                initialization = socket.get_source_initialization()
            parameters.append(initialization)

        return transpiler.call(function, source_name, parameters, post_parameter_initialization)


class MaltIONode(bpy.types.Node, MaltNode):
    
    bl_label = "IO Node"

    properties: bpy.props.PointerProperty(type=MaltPropertyGroup)
    is_output: bpy.props.BoolProperty()

    def malt_setup(self):
        function = self.get_function()
        if self.first_setup:
            self.name = self.io_type + (' Output' if self.is_output else ' Input')

        inputs = {}
        outputs = {}
        
        if function['type'] != 'void' and self.is_output:
            inputs['result'] = {'type': function['type']}
        for parameter in function['parameters']:
            if parameter['io'] in ['out','inout'] and self.is_output:
                if parameter['io'] == 'inout':
                    if 'meta' not in parameter: parameter['meta'] = {}
                    parameter['meta']['init'] = parameter['name']
                inputs[parameter['name']] = parameter
            if parameter['io'] in ['','in','inout'] and self.is_output == False:
                outputs[parameter['name']] = parameter
        
        self.setup_sockets(inputs, outputs)

    io_type : bpy.props.StringProperty(update=MaltNode.setup)

    def get_function(self):
        graph = self.id_data.get_pipeline_graph()
        return graph.graph_IO[self.io_type]

    def get_source_socket_reference(self, socket):
        io = 'out' if self.is_output else 'in'
        return self.id_data.get_transpiler().io_parameter_reference(socket.name, io)
    
    def get_source_code(self, transpiler):
        code = ''
        if self.is_output:
            function = self.get_function()
            for socket in self.inputs:
                if socket.name == 'result':
                    code += transpiler.declaration(socket.data_type, socket.array_size, socket.name)
                initialization = socket.get_source_initialization()
                if initialization:
                    code += transpiler.asignment(socket.get_source_reference(), initialization)

            if function['type'] != 'void':
                code += transpiler.result(self.inputs['result'].get_source_reference())

        return code


class MaltInlineNode(bpy.types.Node, MaltNode):
    
    bl_label = "Inline Code Node"

    def code_update(self, context):
        #update the node tree
        self.id_data.update()

    code : bpy.props.StringProperty(update=code_update)

    def on_socket_update(self, socket):
        self.update()
        self.id_data.update()

    def malt_init(self):
        self.setup()

    def malt_setup(self):
        if self.first_setup:
            self.name = 'Inline Code'
        self.malt_update()
    
    def malt_update(self):
        last = 0
        for i, input in enumerate(self.inputs):
            if input.data_type != '' or input.get_linked():
                last = i + 1
        variables = 'abcdefgh'[:min(last+1,8)]
        
        inputs = {}
        for var in variables:
            inputs[var] = {'type': ''}
            if var in self.inputs:
                input = self.inputs[var]
                linked = self.inputs[var].get_linked()
                if linked and linked.data_type != '':
                    inputs[var] = {'type': linked.data_type, 'size': linked.array_size}
                else:
                    inputs[var] = {'type': input.data_type, 'size': input.array_size}
        
        outputs = { 'result' : {'type': ''} }
        if 'result' in self.outputs:
            out = self.outputs['result'].get_linked()
            if out:
                outputs['result'] = {'type': out.data_type, 'size': out.array_size}
        
        self.setup_sockets(inputs, outputs)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'code', text='')
    
    def draw_socket(self, context, layout, socket, text):
        if socket.is_output == False:
            layout = layout.split(factor=0.66)
            row = layout.row(align=True).split(factor=0.1)
            row.alignment = 'LEFT'
            MaltNode.draw_socket(self, context, row, socket, socket.name)
            layout.prop(socket, 'data_type', text='')
        else:
            MaltNode.draw_socket(self, context, layout, socket, socket.name)

    def get_source_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_source_name(), socket.name)
    
    def get_source_code(self, transpiler):
        code = ''
        result_socket = self.outputs['result']
        code += transpiler.declaration(result_socket.data_type, result_socket.array_size, result_socket.get_source_reference())

        scoped_code = ''
        for input in self.inputs:
            if input.data_type != '':
                initialization = input.get_source_initialization()
                scoped_code += transpiler.declaration(input.data_type, input.array_size, input.name, initialization)
        if self.code != '':
            scoped_code += transpiler.asignment(self.outputs['result'].get_source_reference(), self.code)

        return code + transpiler.scoped(scoped_code)


class MaltArrayIndexNode(bpy.types.Node, MaltNode):
    
    bl_label = "Array Index Node"

    def malt_init(self):
        self.setup()
        
    def malt_setup(self):
        if self.first_setup:
            self.name = 'Array Index'
        self.setup_sockets({ 'array' : {'type': '', 'size': 1}, 'index' : {'type': Parameter(0, Type.INT) }},
            {'element' : {'type': ''} })
        
    def malt_update(self):
        inputs = { 
            'array' : {'type': '', 'size': 1},
            'index' : {'type': Parameter(0, Type.INT) }
        }
        outputs = { 'element' : {'type': ''} }
        
        linked = self.inputs['array'].get_linked()
        if linked and linked.array_size > 0:
            inputs['array']['type'] = linked.data_type
            inputs['array']['size'] = linked.array_size
            outputs['element']['type'] = linked.data_type

        self.setup_sockets(inputs, outputs)

    def get_source_socket_reference(self, socket):
        return '{}_0_{}'.format(self.get_source_name(), socket.name)
    
    def get_source_code(self, transpiler):
        array = self.inputs['array']
        index = self.inputs['index']
        element = self.outputs['element']
        element_reference = index.get_source_global_reference()
        if index.get_linked():
            element_reference = index.get_linked().get_source_reference()
        initialization = '{}[{}]'.format(array.get_linked().get_source_reference(), element_reference)
        return transpiler.declaration(element.data_type, element.array_size, element.get_source_reference(), initialization)



class NODE_PT_MaltNodeTree(bpy.types.Panel):

    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Malt Nodes"
    bl_label = "Malt Node Tree UI"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MaltTree'
    
    def draw(self, context):
        layout = self.layout
        #layout.prop(context.space_data.node_tree, 'generated_source')


def preload_menus(structs, functions):
    files = set()
    for name, struct in structs.items():
        files.add(struct['file'])
    for file in files:
        get_structs_menu(file)
    
    files = set()
    for name, function in functions.items():
        files.add(function['file'])
    for file in files:
        get_functions_menu(file)
        

def insert_node(layout, type, label, settings = {}):
    operator = layout.operator("node.add_node", text=label)
    operator.type = type
    operator.use_transform = True
    for name, value in settings.items():
        item = operator.settings.add()
        item.name = name
        item.value = value
    return operator

__FUNCTION_MENUES = {}

def get_functions_menu(file):
    global __FUNCTION_MENUES

    if file not in __FUNCTION_MENUES.keys():
        file_to_label = file.replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
        class_name = 'MALT_MT_functions_' + str(len(__FUNCTION_MENUES))
        
        def draw(self, context):
            graph = get_pipeline_graph(context)
            if graph:
                library_functions = context.space_data.node_tree.get_library()['functions']
                for name, function in chain(graph.functions.items(), library_functions.items()):
                    if function['file'] == file:
                        insert_node(self.layout, "MaltFunctionNode", name.replace('_', ' '), settings={
                            'function_type' : repr(name)
                        })

        menu_type = type(class_name, (bpy.types.Menu,), {
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": file_to_label,
            "draw": draw,
        })
        bpy.utils.register_class(menu_type)

        __FUNCTION_MENUES[file] = class_name
    
    return __FUNCTION_MENUES[file]

__STRUCT_MENUES = {}

def get_structs_menu(file):
    global __STRUCT_MENUES

    if file not in __STRUCT_MENUES:
        file_to_label = file.replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
        class_name = 'MALT_MT_structs_' + str(len(__STRUCT_MENUES))

        def draw(self, context):
            graph = get_pipeline_graph(context)
            if graph:
                library_structs = context.space_data.node_tree.get_library()['structs']
                for name, struct in chain(graph.structs.items(), library_structs.items()):
                    if struct['file'] == file:
                        insert_node(self.layout, "MaltStructNode", name.replace('_', ' '), settings={
                            'struct_type' : repr(name)
                        })

        menu_type = type(class_name, (bpy.types.Menu,), {
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": file_to_label,
            "draw": draw,
        })
        bpy.utils.register_class(menu_type)

        __STRUCT_MENUES[file] = class_name
    
    return __STRUCT_MENUES[file]


class MALT_MT_NodeFunctions(bpy.types.Menu):
    
    bl_label = "Malt Node Functions Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            files = set()
            library_functions = context.space_data.node_tree.get_library()['functions']
            for name, function in chain(library_functions.items(), graph.functions.items()):
                files.add(function['file'])
            for file in sorted(files):
                self.layout.menu(get_functions_menu(file))

class MALT_MT_NodeStructs(bpy.types.Menu):
    
    bl_label = "Malt Node Structs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            files = set()
            library_structs = context.space_data.node_tree.get_library()['structs']
            for name, struct in chain(library_structs.items(), graph.structs.items()):
                files.add(struct['file'])
            for file in sorted(files):
                self.layout.menu(get_structs_menu(file))

class MALT_MT_NodeInputs(bpy.types.Menu):
    
    bl_label = "Malt Node Inputs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Input', settings={
                    'is_output' : repr(False),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOutputs(bpy.types.Menu):
    
    bl_label = "Malt Node Outputs Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            for name in sorted(graph.graph_IO):
                insert_node(self.layout, "MaltIONode", name + ' Ouput', settings={
                    'is_output' : repr(True),
                    'io_type' : repr(name),
            })

class MALT_MT_NodeOther(bpy.types.Menu):
    
    bl_label = "Malt Node Other Menu"

    def draw(self, context):
        graph = get_pipeline_graph(context)
        if graph:
            insert_node(self.layout, "MaltInlineNode", 'Inline Code')
            insert_node(self.layout, "MaltArrayIndexNode", 'Array Index')

def add_node_ui(self, context):
    if context.space_data.tree_type != 'MaltTree':
        return
    if context.space_data.node_tree is None:
        self.layout.label(text='No active node tree')
        return
    if context.space_data.node_tree.graph_type == '':
        self.layout.label(text='No graph type selected')
        return
    graph = get_pipeline_graph(context)
    if graph:
        self.layout.menu("MALT_MT_NodeFunctions", text='Functions')
        self.layout.menu("MALT_MT_NodeStructs", text='Structs')
        self.layout.menu("MALT_MT_NodeInputs", text='Inputs')
        self.layout.menu("MALT_MT_NodeOutputs", text='Outputs')
        self.layout.menu("MALT_MT_NodeOther", text='Other')

def node_header_ui(self, context):
    if context.space_data.tree_type != 'MaltTree' or context.space_data.node_tree is None:
        return
    #self.layout.use_property_split=True
    #self.layout.alignment = 'LEFT'
    self.layout.prop(context.space_data.node_tree, 'library_source',text='')
    self.layout.prop_search(context.space_data.node_tree, 'graph_type', context.scene.world.malt, 'graph_types',text='')
    #self.layout.prop(context.space_data.node_tree, 'edit_material',text='')

    
classes = (
    MaltTree,
    NODE_PT_MaltNodeTree,
    MaltSocket,
    #MaltNode,
    MaltStructNode,
    MaltFunctionNode,
    MaltIONode,
    MaltInlineNode,
    MaltArrayIndexNode,
    MALT_MT_NodeFunctions,
    MALT_MT_NodeStructs,
    MALT_MT_NodeInputs,
    MALT_MT_NodeOutputs,
    MALT_MT_NodeOther,
)

def register():
    for _class in classes: bpy.utils.register_class(_class)

    bpy.types.NODE_MT_add.append(add_node_ui)
    bpy.types.NODE_HT_header.append(node_header_ui)

    bpy.app.timers.register(track_library_changes, persistent=True)
    

def unregister():
    bpy.types.NODE_MT_add.remove(add_node_ui)
    bpy.types.NODE_HT_header.remove(node_header_ui)

    for _class in reversed(classes): bpy.utils.unregister_class(_class)

    bpy.app.timers.unregister(track_library_changes)

