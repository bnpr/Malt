class PipelineNode():

    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    @staticmethod
    def get_pass_type():
        return None
    
    @classmethod
    def static_reflect(cls, name, inputs, outputs):
        meta = {}
        if cls.__doc__:
            meta['doc'] = cls.__doc__
        dictionary = {
            'name' : name,
            'type' : 'void',
            'file' : 'Render',
            'parameters' : [],
            'pass_type' : cls.get_pass_type(),
            'meta' : meta,
        }
        for name, input in inputs.items():
            meta = {}
            if input.doc:
                meta['doc'] = input.doc
            if input.subtype:
                meta['subtype'] = input.subtype
            if input.default_value is not None and input.default_value != input.type_string():
                meta['default'] = input.default_value
            dictionary['parameters'].append({
                'name' : name,
                'type' : input,
                'size' : input.size,
                'io' : 'in',
                'meta' : meta,
            })
        for name, output in outputs.items():
            meta = {}
            if output.doc:
                meta['doc'] = output.doc
            if output.subtype:
                meta['subtype'] = output.subtype
            if output.default_value is not None and output.default_value != output.type_string():
                meta['default'] = output.default_value
            dictionary['parameters'].append({
                'name' : name,
                'type' : output,
                'size' : output.size,
                'io' : 'out',
                'meta' : {},
            })
        return dictionary
    
    @classmethod
    def reflect(cls):
        return cls.static_reflect(cls.__name__, cls.reflect_inputs(), cls.reflect_outputs())

    @classmethod
    def reflect_inputs(cls):
        return {}

    @classmethod
    def reflect_outputs(cls):
        return {}
    
    def execute(self, parameters):
        pass
