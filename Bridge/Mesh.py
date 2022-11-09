MESHES = {}

def load_mesh(pipeline, msg):
    name = msg['name']
    data = msg['data']

    MESHES[name] = pipeline.load_mesh(
        position = data['positions'],
        indices = data['indices'],
        normal = data['normals'],
        tangent = data['tangents'],
        uvs = data['uvs'],
        colors = data['colors']
    )
