import ctypes, logging as LOG, io, sys
from Bridge.ipc import SharedBuffer

def bridge_method(function):
    def result(*args, **kwargs):
        self = args[0]
        try:
            if self.lost_connection == False:
                return function(*args, **kwargs)
        except:
            import traceback
            LOG.error(traceback.format_exc())
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
        LOG.log(self.log_level, s)
        return super().write(s)

class Bridge():

    def __init__(self, pipeline_path, viewport_bit_depth=8, debug_mode=False, renderdoc_path=None, plugins_paths=[], docs_path=None):
        super().__init__()

        import sys
        if not isinstance(sys.stdout, IOCapture):
            import os, tempfile, time
            date = time.strftime("%Y-%m-%d(%H-%M)")
            log_path = os.path.join(tempfile.gettempdir(),'malt ' + date + '.log')
            LOG.basicConfig(filename=log_path, level=LOG.DEBUG, format='Blender > %(message)s')
            sys.stdout = IOCapture(sys.stdout, log_path, LOG.INFO)
            sys.stderr = IOCapture(sys.stderr, log_path, LOG.ERROR)
            LOG.info('SETUP IOCapture')
        
        import multiprocessing, random, string
        mp = multiprocessing.get_context('spawn')

        self.viewport_bit_depth = viewport_bit_depth

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
        self.shared_buffers = []
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

        for name in ['MAIN','REFLECTION']: add_connection(name)

        from . import start_server
        self.process = mp.Process(target=start_server, kwargs={
            'pipeline_path': pipeline_path, 
            'viewport_bit_depth': viewport_bit_depth, 
            'connection_addresses': malt_to_bridge, 
            'shared_dic': self.shared_dict,
            'lock': self.lock,
            'log_path': sys.stdout.log_path,
            'debug_mode': debug_mode,
            'renderdoc_path': renderdoc_path,
            'plugins_paths': plugins_paths,
            'docs_path': docs_path,
        })
        self.process.daemon = True
        self.process.start()

        for name, listener in listeners.items():
            bridge_to_malt[name] = listener.accept()
        
        self.connections = bridge_to_malt

        params = self.connections['MAIN'].recv()
        assert(params['msg_type'] == 'PARAMS')
        self.parameters = params['params']
        self.graphs = params['graphs']
        self.render_outputs = params['outputs']
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
    def compile_material(self, path, search_paths=[], custom_passes=[]):
        self.connections['MAIN'].send({
            'msg_type': 'MATERIAL',
            'path': path,
            'search_paths': search_paths,
            'custom_passes': custom_passes,
        })
        return self.connections['MAIN'].recv()

    @bridge_method
    def compile_materials(self, paths, search_paths=[], async_compilation=False):
        for path in paths:
            self.connections['MAIN'].send({
                'msg_type': 'MATERIAL',
                'path': path,
                'search_paths': search_paths,
                'custom_passes': [],
            })
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
                msg = self.connections['MAIN'].recv()
                assert(msg['msg_type'] == 'MATERIAL')
                material = msg['material']
                results[material.path] = material
                received.append(material.path)
        return results
    
    @bridge_method
    def receive_async_compilation_materials(self):
        results = {}
        while self.connections['MAIN'].poll():
            msg = self.connections['MAIN'].recv()
            assert(msg['msg_type'] == 'MATERIAL')
            material = msg['material']
            results[material.path] = material
        return results
    
    @bridge_method
    def reflect_source_libraries(self, paths):
        self.connections['REFLECTION'].send({
            'msg_type': 'SHADER REFLECTION',
            'paths': paths
        })
        return self.connections['REFLECTION'].recv()
    
    @bridge_method
    def reload_graphs(self, graph_types):
        self.connections['REFLECTION'].send({
            'msg_type': 'GRAPH RELOAD',
            'graph_types': graph_types
        })
        self.graphs.update(self.connections['REFLECTION'].recv())
    
    @bridge_method
    def get_shared_buffer(self, ctype, size):
        from . import ipc
        #return ipc.SharedBuffer(ctype, size)
        requested_size = ctypes.sizeof(ctype) * size
        reuse_buffer = None
        for buffer in self.shared_buffers:
            release_flag = ctypes.c_bool.from_address(buffer._release_flag.data)
            min_ref_count = 3 # shared_buffers + local buffer var + getrefcount ref
            if release_flag.value == True and sys.getrefcount(buffer) == min_ref_count:
                if buffer._buffer.size >= requested_size:
                    if reuse_buffer is None or buffer._buffer.size < reuse_buffer._buffer.size:
                        reuse_buffer = buffer
        
        if reuse_buffer is None:
            min_size = 1024*1024
            new_size = max(requested_size * 2, min_size)
            reuse_buffer = ipc.SharedBuffer(ctypes.c_byte, new_size)
            self.shared_buffers.append(reuse_buffer)
        
        ctypes.c_bool.from_address(reuse_buffer._release_flag.data).value = True
        reuse_buffer._ctype = ctype
        reuse_buffer._size = size
        return reuse_buffer

    @bridge_method
    def load_mesh(self, name, mesh_data):
        self.connections['MAIN'].send({
            'msg_type': 'MESH',
            'name': name,
            'data': mesh_data
        })
    
    @bridge_method
    def load_texture(self, name, buffer, resolution, channels, sRGB):
        self.connections['MAIN'].send({
            'msg_type': 'TEXTURE',
            'buffer': buffer,
            'name': name,
            'resolution': resolution,
            'channels': channels,
            'sRGB' : sRGB,
        })

    @bridge_method
    def load_gradient(self, name, pixels, nearest):
        self.connections['MAIN'].send({
            'msg_type': 'GRADIENT',
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
    def render(self, viewport_id, resolution, scene, scene_update, renderdoc_capture=False, AOVs={}):
        assert(viewport_id in self.viewport_ids or viewport_id == 0)

        new_buffers = None
        buffers = self.render_buffers.get(viewport_id)
        if buffers is None or buffers['__resolution'] != resolution or buffers['__AOVs'] != AOVs:
            self.render_buffers[viewport_id] = {
                '__resolution' : resolution,
                '__AOVs' : AOVs
            }
            from itertools import chain
            for key, texture_format in chain(self.render_outputs.items(), AOVs.items()):
                buffer_type = ctypes.c_float
                if viewport_id != 0:
                    if self.viewport_bit_depth == 8:
                        buffer_type = ctypes.c_byte
                    elif self.viewport_bit_depth == 16:
                        buffer_type = ctypes.c_ushort
                w,h = resolution
                self.render_buffers[viewport_id][key] = self.get_shared_buffer(buffer_type, w*h*4)
                if viewport_id != 0: #viewport render
                    #we only need the color buffer
                    break
            new_buffers = self.render_buffers[viewport_id]

        if (viewport_id, 'SETUP') in self.shared_dict:
            import time
            start = time.perf_counter()
            while self.shared_dict[(viewport_id, 'SETUP')] == False:
                # Don't stack multiple render workloads for the same viewport
                if time.perf_counter() - start > 1:
                    #But don't stall Blender forever
                    if new_buffers is None and scene_update == False:
                        #Never skip new_buffers setup or scene update
                        return
                    else:
                        break
                
        self.shared_dict[(viewport_id, 'FINISHED')] = None
        self.connections['MAIN'].send({
            'msg_type': 'RENDER',
            'viewport_id': viewport_id,
            'resolution': resolution,
            'scene': scene,
            'scene_update': scene_update,
            'new_buffers': new_buffers,
            'renderdoc_capture' : renderdoc_capture,
        })
        self.shared_dict[(viewport_id, 'SETUP')] = False

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
