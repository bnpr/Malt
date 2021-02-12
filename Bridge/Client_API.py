import ctypes, time
import multiprocessing as mp

import Malt.Scene as Scene
import Malt.Parameter as Parameter

import socket

__MALT_PROCESS = None
__CONNECTIONS = {}
__MANAGER = None
__SHARED_DIC = None

import socket as socket_lib
import multiprocessing.connection as connection

def server_start(pipeline_path): #TODO: Pass include/import paths
    server_terminate()
    
    global __MANAGER, __SHARED_DIC
    __MANAGER = mp.Manager()
    __SHARED_DIC = __MANAGER.dict()

    listeners = {}
    bridge_to_malt = {}
    malt_to_bridge = {}
    
    def add_connection(name):
        address = ('localhost', 0)
        listener = connection.Listener(address)
        address = listener.address
        listeners[name] = listener
        malt_to_bridge[name] = address

    for name in ['PARAMS','MESH','MATERIAL','TEXTURE','GRADIENT','RENDER']: add_connection(name)

    from . import Server
    
    global __MALT_PROCESS
    __MALT_PROCESS = mp.Process(target=Server.main, args=[pipeline_path, malt_to_bridge, __SHARED_DIC])
    __MALT_PROCESS.daemon = True
    __MALT_PROCESS.start()

    for name, listener in listeners.items():
        bridge_to_malt[name] = listener.accept()
    
    global __CONNECTIONS 
    __CONNECTIONS = bridge_to_malt

    return __CONNECTIONS['PARAMS'].recv()

def server_terminate():
    if __MALT_PROCESS:
        __MALT_PROCESS.terminate()

def compile_material(path, search_paths=[]):
    __CONNECTIONS['MATERIAL'].send({'path': path, 'search_paths': search_paths})
    return __CONNECTIONS['MATERIAL'].recv()

def compile_materials(paths, search_paths=[]):
    for path in paths:
        __CONNECTIONS['MATERIAL'].send({'path': path, 'search_paths': search_paths})
    results = {}
    for path in paths:
        results[path] = __CONNECTIONS['MATERIAL'].recv()
    return results

def load_mesh(name, mesh_data):
    __CONNECTIONS['MESH'].send({
        'name': name,
        'data': mesh_data
    })

def get_texture_buffer(pixels_times_channels):
    import Bridge.ipc as ipc
    '''
    while __SHARED_DIC['TEXTURE_LOCK']:
        pass
    '''
    return ipc.load_shared_buffer('TEXTURE_BUFFER', ctypes.c_float, pixels_times_channels)

def load_texture(name, resolution, channels, sRGB):
    import Bridge.ipc as ipc
    __SHARED_DIC['TEXTURE_LOCK'] = True
    __CONNECTIONS['TEXTURE'].send({
        'buffer_name': ipc.get_shared_buffer_full_name('TEXTURE_BUFFER'),
        'name': name,
        'resolution': resolution,
        'channels': channels,
        'sRGB' : sRGB,
    })

def load_gradient(name, pixels, nearest):
    import Bridge.ipc as ipc
    __CONNECTIONS['GRADIENT'].send({
        'name': name,
        'pixels': pixels,
        'nearest' : nearest,
    })

__VIEWPORT_IDs = []

def get_viewport_id():
    i = 1 #0 is reserved for F12
    while True:
        if i not in __VIEWPORT_IDs:
            __VIEWPORT_IDs.append(i)
            return i
        i+=1

def free_viewport_id(viewport_id):
    __VIEWPORT_IDs.remove(viewport_id)

__RENDER_BUFFERS = {}

def render(viewport_id, resolution, scene, scene_update):
    import Bridge.ipc as ipc
    #TODO: Per session unique name
    name = str(viewport_id)
    w,h = resolution
    __RENDER_BUFFERS[viewport_id] = ipc.load_shared_buffer(name, ctypes.c_float, w*h*4)
    __SHARED_DIC[(viewport_id, 'FINISHED')] = None
    __CONNECTIONS['RENDER'].send({
        'viewport_id': viewport_id,
        'resolution': resolution,
        'scene': scene,
        'scene_update': scene_update,
        'buffer_name': ipc.get_shared_buffer_full_name(name),
    })

def render_result(viewport_id):
    finished = False

    if (viewport_id, 'FINISHED') in __SHARED_DIC:
        finished = __SHARED_DIC[(viewport_id, 'FINISHED')] == True
    
    if viewport_id in __RENDER_BUFFERS.keys():
        return __RENDER_BUFFERS[viewport_id], finished
    else:
        return None, finished

