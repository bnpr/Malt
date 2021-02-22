import ctypes

import Malt.Scene as Scene
import Malt.Parameter as Parameter

def bridge_method(function):
    def result(*args, **kwargs):
        self = args[0]
        try:
            if self.lost_connection == False:
                return function(*args, **kwargs)
        except:
            import traceback
            print(traceback.print_exc())
            self.lost_connection = True
        return None
    return result

class Bridge(object):

    def __init__(self, pipeline_path, timeout=5):
        super().__init__()
        
        import multiprocessing as mp
        import random, string

        self.manager = mp.Manager()
        self.shared_dict = self.manager.dict()
        self.connections = {}
        self.process = None
        self.lost_connection = True
        self.parameters = {}
        self.render_buffers = {}
        self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

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

        for name in ['PARAMS','MESH','MATERIAL','TEXTURE','GRADIENT','RENDER']: add_connection(name)

        from . import Server
        self.process = mp.Process(target=Server.main, args=[pipeline_path, malt_to_bridge, self.shared_dict])
        self.process.daemon = True
        self.process.start()

        for name, listener in listeners.items():
            bridge_to_malt[name] = listener.accept()
        
        self.connections = bridge_to_malt

        if self.connections['PARAMS'].poll(timeout):
            self.parameters = self.connections['PARAMS'].recv()
            self.lost_connection = False
    
    def __del__(self):
        if self.process:
            self.process.terminate()
    
    def get_parameters(self):
        return self.parameters

    @bridge_method
    def compile_material(self, path, search_paths=[]):
        self.connections['MATERIAL'].send({'path': path, 'search_paths': search_paths})
        return self.connections['MATERIAL'].recv()

    @bridge_method
    def compile_materials(self, paths, search_paths=[]):
        for path in paths:
            self.connections['MATERIAL'].send({'path': path, 'search_paths': search_paths})
        results = {}
        for path in paths:
            results[path] = self.connections['MATERIAL'].recv()
        return results

    @bridge_method
    def load_mesh(self, name, mesh_data):
        self.connections['MESH'].send({
            'name': name,
            'data': mesh_data
        })
    
    @bridge_method
    def get_texture_buffer(self, pixels_times_channels):
        buffer_name = 'MALT_TEXTURE_BUFFER_' + self.id
        import Bridge.ipc as ipc
        return ipc.load_shared_buffer(buffer_name, ctypes.c_float, pixels_times_channels)
    
    @bridge_method
    def load_texture(self, name, resolution, channels, sRGB):
        buffer_name = 'MALT_TEXTURE_BUFFER_' + self.id
        import Bridge.ipc as ipc
        self.connections['TEXTURE'].send({
            'buffer_name': ipc.get_shared_buffer_full_name(buffer_name),
            'name': name,
            'resolution': resolution,
            'channels': channels,
            'sRGB' : sRGB,
        })
        #TODO: Recv at the beginning, so it only locks when needed
        self.connections['TEXTURE'].recv()

    @bridge_method
    def load_gradient(self, name, pixels, nearest):
        self.connections['GRADIENT'].send({
            'name': name,
            'pixels': pixels,
            'nearest' : nearest,
        })

    viewport_ids = []

    @bridge_method
    def get_viewport_id(self):
        i = 1 #0 is reserved for F12
        while True:
            if i not in Bridge.viewport_ids:
                Bridge.viewport_ids.append(i)
                return i
            i+=1

    @bridge_method
    def free_viewport_id(self, viewport_id):
        Bridge.viewport_ids.remove(viewport_id)

    @bridge_method
    def render(self, viewport_id, resolution, scene, scene_update):
        buffer_name = 'MALT_RENDER_BUFFER_' + str(viewport_id) + '_' + self.id
        w,h = resolution
        import Bridge.ipc as ipc
        self.render_buffers[viewport_id] = ipc.load_shared_buffer(buffer_name, ctypes.c_float, w*h*4)
        self.shared_dict[(viewport_id, 'FINISHED')] = None
        self.connections['RENDER'].send({
            'viewport_id': viewport_id,
            'resolution': resolution,
            'scene': scene,
            'scene_update': scene_update,
            'buffer_name': ipc.get_shared_buffer_full_name(buffer_name),
        })

    @bridge_method
    def render_result(self, viewport_id):
        finished = False
        if (viewport_id, 'FINISHED') in self.shared_dict:
            finished = self.shared_dict[(viewport_id, 'FINISHED')] == True
        if viewport_id in self.render_buffers.keys():
            return self.render_buffers[viewport_id], finished
        else:
            return None, finished

