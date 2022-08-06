def build_docs(pipeline, docs_path):
    import os
    output_path = os.path.join(docs_path, 'reference')
    parameters = pipeline.get_parameters()
    graphs = pipeline.get_graphs()

    def clean_str(str):
        return ''.join(line.lstrip() for line in str.strip().splitlines(True))

    parameters_result = "# Malt Settings\n"

    def parameters_string(name, parameters):
        if len(parameters) == 0:
            return
        nonlocal parameters_result
        parameters_result += f"## {name}\n"
        stack = []
        for key, parameter in parameters.items():
            if '@' in key:
                continue
            _stack = key.split('.')[:-1]
            for i, e in enumerate(_stack):
                if i+1 > len(stack) or e != stack[i]:
                    parameters_result += '\t'*i + f"- **{e}**\n"
            stack = _stack
            key = key.split('.')[-1]

            tabs = '\t'*len(stack) if stack else ''

            parameters_result += f"{tabs}- **{key}** *: ( {parameter.type_string()} )*"
            default = parameter.default_value
            if default is None or default == '':
                default = 'None'
            elif isinstance(default, tuple):
                default = default[1]
            parameters_result += f'* = {default}*  \n'
            if parameter.doc:
                parameters_result += f'{tabs}>' + clean_str(parameter.doc) + "\n"
    
    parameters_string('Scene', parameters.scene)
    parameters_string('World', parameters.world)
    parameters_string('Camera', parameters.camera)
    parameters_string('Object', parameters.object)
    parameters_string('Material', parameters.material)
    parameters_string('Mesh', parameters.mesh)
    parameters_string('Light', parameters.light)

    open(os.path.join(output_path, 'settings.md'), 'w').write(parameters_result)
    
    from textwrap import indent

    for graph in graphs.values():
        result = f"# {graph.name} Graph Reference\n"
        if len(graph.functions) > 0:
            categories = {
                'Input' : {},
                'Parameters' : {},
                'Math' : {},
                'Vector' : {},
                'Color' : {},
                'Texturing' : {},
                'Shading' : {},
                'Filter' : {},
                'Other' : {},
                'Node Tree' : {},
            }
            for key, function in graph.functions.items():
                if function['meta'].get('internal'):
                    continue

                category = function['meta'].get('category')
                if category is None:
                    category = function['file'].replace('\\', '/').replace('/', ' - ').replace('.glsl', '').replace('_',' ')
                if category not in categories:
                    categories[category] = {}
                subcategory = function['meta'].get('subcategory')
                if subcategory:
                    if subcategory not in categories[category]:
                        categories[category][subcategory] = []
                    categories[category][subcategory].append(function)
                else:
                    categories[category][key] = function

            def draw_function(function, depth=3):
                nonlocal result
                result += '---\n'
                result += f"{'#'*depth} **{function['meta'].get('label', function['name'])}**\n"
                
                if pass_type := function.get('pass_type'):
                    result += f">Graph Type / Pass : *{pass_type.replace('.', ' / ')}*\n\n"

                if doc := function['meta'].get('doc'):
                    result += clean_str(doc) + "\n\n"
                
                inputs = {}
                outputs = {}
                if function['type'] != 'void':
                    outputs['result'] = {'type': function['type'], 'meta':{}}

                for parameter in function['parameters']:
                    label = parameter['meta'].get('label', parameter['name'])
                    if parameter['io'] in ('in', 'inout'):
                        inputs[label] = parameter
                    if parameter['io'] in ('out', 'inout'):
                        outputs[label] = parameter
                
                def draw_params(type, dict):
                    if len(dict) == 0:
                        return
                    nonlocal result
                    result += f"- **{type}**  \n"
                    params = ""
                    for key, parameter in dict.items():
                        if '@' in key:
                            continue
                        try:
                            type = parameter['type'].type_string()
                        except:
                            type = parameter['type']
                        if subtype := parameter['meta'].get('subtype'):
                            type += f' | {subtype}'
                        
                        type = f'( {type} )'

                        if default := parameter['meta'].get('default'):
                            type += f' - default = {default}'
                        
                        params += f"- **{key}** *: {type}*  \n"

                        if doc := parameter['meta'].get('doc'):
                            params += '>' + clean_str(doc) + "\n"
                    
                    result += indent(params, '\t')
                
                draw_params('Inputs', inputs)
                draw_params('Outputs', outputs)
            
            for category, items in categories.items():
                if len(items) == 0:
                    continue
                result += '---\n'
                result += f"## {category}\n"

                for k, v in items.items():
                    if isinstance(v, dict):
                        draw_function(v)
                    else:
                        result += '---\n'
                        result += f"### **{k}**\n"
                        for subcategory_function in v:
                            draw_function(subcategory_function, 4)
        
            open(os.path.join(output_path, f'{graph.name}-graph.md'), 'w').write(result)

                
                


