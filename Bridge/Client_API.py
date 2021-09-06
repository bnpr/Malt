# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes, logging as log, io
from Bridge.ipc import SharedBuffer

def bridge_method(function):
    def result(*args, **kwargs):
        self = args[0]
        try:
            if self.lost_connection == False:
                return function(*args, **kwargs)
        except:
            import traceback
            log.error(traceback.format_exc())
            self.lost_connection = True
        return None
    return result

class IOCapture(io.StringIO):
    def __init__(self, parent, log_path, log_level):
        super().__init__()
        self.parent = parent
        self.log_path = log_path
        self.log_level = log_level
    
    def write(self, s):
        self.parent.write(s)
        log.log(self.log_level, s)
        return super().write(s)

class Bridge(object):

    def __init__(self, pipeline_path, debug_mode=False, renderdoc_path=None):
        super().__init__()

        import sys
        if not isinstance(sys.stdout, IOCapture):
            import os, tempfile, time
            date = time.strftime("%Y-%m-%d(%H-%M)")
            log_path = os.path.join(tempfile.gettempdir(),'malt ' + date + '.log')
            log.basicConfig(filename=log_path, level=log.DEBUG, format='Blender > %(message)s')
            sys.stdout = IOCapture(sys.stdout, log_path, log.INFO)
            sys.stderr = IOCapture(sys.stderr, log_path, log.ERROR)
            log.info('SETUP IOCapture')
        
        import multiprocessing, random, string
        mp = multiprocessing.get_context('spawn')

        self.manager = mp.Manager()
        self.shared_dict = self.manager.dict()
        self.lock = None
        #SharedBuffer.setup_class(self.manager)
        self.connections = {}
        self.process = None
        self.lost_connection = True
        self.parameters = {}
        self.graphs = {}
        self.render_outputs = {}
        self.render_buffers = {}
        self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        self.viewport_ids = []

        listeners = {}
        bridge_to_malt = {}
        malt_to_bridge = {}
        
        import multiprocessing.connection as connection
        def add_connection(name):
            address = ('localhost', 0)
            listener = connection.Listener(address)
            address = listener.address
            listeners[name] = listener
            malt_to_bridge[name] = address

        for name in ['PARAMS','MESH','MATERIAL','SHADER REFLECTION','TEXTURE','GRADIENT','RENDER']: add_connection(name)

        from . import start_server
        self.process = mp.Process(target=start_server, args=[pipeline_path, malt_to_bridge, self.shared_dict, self.lock, sys.stdout.log_path, debug_mode, renderdoc_path])
        self.process.daemon = True
        self.process.start()

        for name, listener in listeners.items():
            bridge_to_malt[name] = listener.accept()
        
        self.connections = bridge_to_malt

        self.parameters, self.graphs, self.render_outputs = self.connections['PARAMS'].recv()
        self.lost_connection = False

    
    def __del__(self):
        if self.process:
            self.process.terminate()
        
    
    def get_parameters(self):
        return self.parameters
    
    @bridge_method
    def get_stats(self):
        if 'STATS' in self.shared_dict and self.shared_dict['STATS']:
            return self.shared_dict['STATS']
        else:
            return ''

    @bridge_method
    def compile_material(self, path, search_paths=[]):
        self.connections['MATERIAL'].send({'path': path, 'search_paths': search_paths})
        return self.connections['MATERIAL'].recv()

    @bridge_method
    def compile_materials(self, paths, search_paths=[], async_compilation=False):
        for path in paths:
            self.connections['MATERIAL'].send({'path': path, 'search_paths': search_paths})
        results = {}
        received = []
        if async_compilation == False:
            while True:
                completed = True
                for path in paths:
                    if path not in received:
                        completed = False
                        break
                if completed:
                    break
                material = self.connections['MATERIAL'].recv()
                results[material.path] = material
                received.append(material.path)
        return results
    
    @bridge_method
    def receive_async_compilation_materials(self):
        results = {}
        while self.connections['MATERIAL'].poll():
            material = self.connections['MATERIAL'].recv()
            results[material.path] = material
        return results
    
    @bridge_method
    def reflect_source_libraries(self, paths):
        self.connections['SHADER REFLECTION'].send({'paths': paths})
        return self.connections['SHADER REFLECTION'].recv()
    
    @bridge_method
    def get_shared_buffer(self, ctype, size):
        from . import ipc
        return ipc.SharedBuffer(ctype, size)

    @bridge_method
    def load_mesh(self, name, mesh_data):
        self.connections['MESH'].send({
            'name': name,
            'data': mesh_data
        })
    
    @bridge_method
    def load_texture(self, name, buffer, resolution, channels, sRGB):
        self.connections['TEXTURE'].send({
            'buffer': buffer,
            'name': name,
            'resolution': resolution,
            'channels': channels,
            'sRGB' : sRGB,
        })

    @bridge_method
    def load_gradient(self, name, pixels, nearest):
        self.connections['GRADIENT'].send({
            'name': name,
            'pixels': pixels,
            'nearest' : nearest,
        })

    @bridge_method
    def get_viewport_id(self):
        i = 1 #0 is reserved for F12
        while True:
            if i not in self.viewport_ids:
                self.viewport_ids.append(i)
                return i
            i+=1

    @bridge_method
    def free_viewport_id(self, viewport_id):
        self.viewport_ids.remove(viewport_id)

    @bridge_method
    def render(self, viewport_id, resolution, scene, scene_update, renderdoc_capture=False):
        assert(viewport_id in self.viewport_ids or viewport_id == 0)

        new_buffers = None
        if viewport_id not in self.render_buffers.keys() or self.render_buffers[viewport_id]['__resolution'] != resolution:
            print('CREATE NEW BUFFERS')
            self.render_buffers[viewport_id] = {'__resolution' : resolution}
            for key, texture_format in self.render_outputs.items():
                w,h = resolution
                self.render_buffers[viewport_id][key] = self.get_shared_buffer(ctypes.c_float, w*h*4)
                if viewport_id != 0: #viewport render
                    #we only need the color buffer
                    break
            new_buffers = self.render_buffers[viewport_id]

        self.shared_dict[(viewport_id, 'FINISHED')] = None
        self.connections['RENDER'].send({
            'viewport_id': viewport_id,
            'resolution': resolution,
            'scene': scene,
            'scene_update': scene_update,
            'new_buffers': new_buffers,
            'renderdoc_capture' : renderdoc_capture,
        })

    @bridge_method
    def render_result(self, viewport_id):
        finished = False
        if (viewport_id, 'FINISHED') in self.shared_dict:
            finished = self.shared_dict[(viewport_id, 'FINISHED')] == True
        
        read_resolution = None
        if (viewport_id, 'READ_RESOLUTION') in self.shared_dict:
            read_resolution = self.shared_dict[viewport_id, 'READ_RESOLUTION']
        
        if viewport_id in self.render_buffers.keys():
            return self.render_buffers[viewport_id], finished, read_resolution
        else:
            return None, finished, read_resolution


