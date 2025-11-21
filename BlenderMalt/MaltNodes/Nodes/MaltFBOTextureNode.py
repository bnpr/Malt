import bpy
from BlenderMalt.MaltNodes.MaltNode import MaltNode

class MaltFBOTextureNode(bpy.types.Node, MaltNode):
    bl_idname = 'MaltFBOTextureNode'
    bl_label = 'FBO Texture'

    fbo_name : bpy.props.StringProperty(name="FBO Name", default="Main Camera")

    @property
    def sanitized_name(self):
        return self.fbo_name.replace('.', '_').replace(' ', '_')

    def malt_setup(self, copy=None):
        inputs = {
            'UV' : {'type': 'vec2', 'size': 0}
        }
        outputs = {
            'Color' : {'type': 'vec4', 'size': 0}
        }
        self.setup_sockets(inputs, outputs)
    
    def draw_buttons(self, context, layout):
        layout.prop(self, "fbo_name", text="FBO Name")
    
    def get_source_code(self, transpiler):
        uv_ref = self.inputs['UV'].get_source_initialization()
        color_ref = self.outputs['Color'].get_source_reference()
        
        # Declare output variable
        code = transpiler.declaration('vec4', 0, color_ref)
        
        # Assign texture sample to output
        assignment = f"{color_ref} = texture({self.sanitized_name}, {uv_ref});"
        
        return code + assignment
    
    def get_source_global_parameters(self, transpiler):
        return f"uniform sampler2D {self.sanitized_name};\n"

classes = [
    MaltFBOTextureNode,
]

def register():
    for _class in classes: bpy.utils.register_class(_class)
    
def unregister():
    for _class in reversed(classes): bpy.utils.unregister_class(_class)
