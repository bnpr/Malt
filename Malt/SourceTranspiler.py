import textwrap

#TODO: Send transpiler along graph types
class SourceTranspiler():
    
    @classmethod
    def get_source_name(self, name, prefix='_'):
        name = name.replace('.','_').replace(' ', '_')
        name = prefix + ''.join(char for char in name if char.isalnum() or char == '_')
        while '__' in name:
            name = name.replace('__','_')
        return name

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
    def custom_io_reference(self, io, graph_io_type, name):
        pass

    @classmethod
    def preprocessor_wrap(self, define, content):
        return content

    @classmethod
    def custom_output_declaration(self, type, name, index, graph_io_type):
        pass

    @classmethod
    def parameter_reference(self, node_name, parameter_name, io_type):
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
        return f"U_0{node_name}_0_{self.get_source_name(parameter_name)}".replace('__','_')

    @classmethod
    def global_declaration(self, type, size, name, initialization=None):
        uniform_declaration = 'uniform '
        if 'sampler' in type:
            uniform_declaration = 'OPTIONALLY_BINDLESS uniform '
        return uniform_declaration + self.declaration(type, size, name, initialization)
    
    @classmethod
    def custom_io_reference(self, io, graph_io_type, name):
        return f"{io.upper()}_{graph_io_type.upper()}_{''.join(char.upper() for char in name if char.isalnum())}"
    
    @classmethod
    def preprocessor_wrap(self, define, content):
        if define is None:
            return content
        return textwrap.dedent('''\
        #ifdef {}
        {}
        #endif //{}
        ''').format(define, content.strip(), define)

    @classmethod
    def custom_output_declaration(self, type, name, index, graph_io_type):
        return f"layout (location = {index}) out {type} {self.custom_io_reference('OUT', graph_io_type, name)};\n"

    @classmethod
    def parameter_reference(self, node_name, parameter_name, io_type):
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
                src_reference = self.parameter_reference(name, parameter['name'], parameter['io'])
                src += self.declaration(parameter['type'], parameter['size'], src_reference, initialization)
                parameters[i] = src_reference
        src += post_parameter_initialization

        initialization = f'{function["name"]}({",".join(parameters)})'
        
        if function['type'] != 'void' and self.is_instantiable_type(function['type']):
            src += self.declaration(function['type'], 0, self.parameter_reference(name, 'result', 'out'), initialization)
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
    def custom_io_reference(self, io, graph_io_type, name):
        return self.io_parameter_reference(name, io)

    @classmethod
    def custom_output_declaration(self, type, name, index, graph_io_type):
        return self.declaration(type, 0, self.io_parameter_reference(name, 'out'))

    @classmethod    
    def parameter_reference(self, node_name, parameter_name, io_type):
        if io_type:
            return f'{node_name}_parameters["{io_type.upper()}"]["{parameter_name}"]'
        else:
            return f'{node_name}_parameters["{parameter_name}"]'

    @classmethod    
    def io_parameter_reference(self, parameter_name, io_type):
        return f'{io_type.upper()}["{parameter_name}"]'

    @classmethod
    def call(self, function, name, parameters=[], post_parameter_initialization = ''):
        import textwrap
        src = ''
        src += textwrap.dedent(f'''
        {name}_parameters = {{
            'IN' : {{}},
            'OUT' : {{}},
        }}
        ''')
        for i, parameter in enumerate(function['parameters']):
            initialization = parameters[i]
            if initialization is None:
                initialization = 'None'
            parameter_reference = self.parameter_reference(name, parameter['name'], parameter['io'])
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
