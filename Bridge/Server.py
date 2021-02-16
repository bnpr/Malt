# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

def setup_logging():
    import logging as log
    #log.basicConfig(filename='test.log', level=log.DEBUG)

import ctypes
import glfw
import Malt
import Malt.Pipelines.NPR_Pipeline.NPR_Pipeline as NPR_Pipeline

from Malt.GL import GL
from Malt.GL.GL import *
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture

import Bridge
from Bridge.Mesh import load_mesh
from Bridge.Render import render
from Bridge.Texture import load_texture, load_gradient

import Bridge.ipc as ipc

class PBO(object):

    def __init__(self):
        self.handle = gl_buffer(GL_INT, 1)
        self.size = None
        self.sync = None
    
    def __del__(self):
        glDeleteBuffers(1, self.handle)
    
    def setup(self, render_target):
        w,h = render_target.resolution
        size = w*h*4*4
        if self.size != size:
            self.size = size
            glDeleteBuffers(1, self.handle)
            glGenBuffers(1, self.handle)
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.handle[0])
            glBufferData(GL_PIXEL_PACK_BUFFER, size, None, GL_STREAM_READ)
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
        
        render_target.bind()
        GL.glReadBuffer(GL.GL_COLOR_ATTACHMENT0)
        
        glBindBuffer(GL_PIXEL_PACK_BUFFER, self.handle[0])
        GL.glReadPixels(0, 0, w, h, GL_RGBA, GL_FLOAT, 0)
        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        if self.sync:
            glDeleteSync(self.sync)
        self.sync = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
    
    def poll(self):
        wait = glClientWaitSync(self.sync, GL_SYNC_FLUSH_COMMANDS_BIT, 0)
        return wait == GL_ALREADY_SIGNALED
    
    def load(self, buffer):
        wait = glClientWaitSync(self.sync, GL_SYNC_FLUSH_COMMANDS_BIT, 0)
        if wait == GL_ALREADY_SIGNALED:
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.handle[0])
            result = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)
            if result:
                ctypes.memmove(buffer, result, self.size)
                glUnmapBuffer(GL_PIXEL_PACK_BUFFER)
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
            return True
        return False


class Viewport(object):

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.buffer = None
        self.resolution = None
        self.scene = None
        self.pbos_active = []
        self.pbos_inactive = []
        self.is_new_frame = True
        self.needs_more_samples = True
    
    def setup(self, buffer, resolution, scene, scene_update):
        if self.resolution != resolution:
            self.pbos_inactive.extend(self.pbos_active)
            self.pbos_active = []
        
        self.buffer = buffer
        self.resolution = resolution

        self.sample_index = 0
        self.is_new_frame = True
        self.needs_more_samples = True
        
        if scene_update or self.scene is None:
            for mesh in scene.meshes:
                for i, submesh in enumerate(mesh):
                    submesh.mesh = Bridge.Mesh.MESHES[submesh.mesh][i]
            
            for material in scene.materials:
                material.shader = Bridge.Material.get_shader(material.shader['path'], material.shader['parameters'])
            
            for obj in scene.objects:
                obj.matrix = (ctypes.c_float * 16)(*obj.matrix)
            
            scene.batches = self.pipeline.build_scene_batches(scene.objects)
            self.scene = scene
        else:
            self.scene.camera = scene.camera
            self.scene.time = scene.time
            self.scene.frame = scene.frame
    
    def render(self):
        if self.needs_more_samples:
            result = self.pipeline.render(self.resolution, self.scene, False, self.is_new_frame)
            self.is_new_frame = False
            self.needs_more_samples = self.pipeline.needs_more_samples()
            
            if True or len(self.pbos_active) < 10 or not self.needs_more_samples: #Avoid too much latency
                pbo = None
                if len(self.pbos_inactive) > 0:
                    pbo = self.pbos_inactive.pop()
                else:
                    pbo = PBO()
                
                pbo.setup(RenderTarget([result['COLOR']]))
                self.pbos_active.append(pbo)

        if len(self.pbos_active) > 0:
            for i, pbo in reversed(list(enumerate(self.pbos_active))):
                if pbo.poll():
                    pbo.load(self.buffer.c.data)
                    self.pbos_inactive.extend(self.pbos_active[:i+1])
                    self.pbos_active = self.pbos_active[i+1:]
                    break
        
        return len(self.pbos_active) > 0

import time
import cProfile, pstats, io
import socket as socket_lib
import multiprocessing.connection as connection

PROFILE = False

def main(pipeline_path, connection_addresses, shared_dic):
    setup_logging()

    import sys, os, psutil
    priority = psutil.REALTIME_PRIORITY_CLASS if sys.platform == 'win32' else -20
    psutil.Process(os.getpid()).nice(priority)

    connections = {}
    for name, address in connection_addresses.items():
        connections[name] = connection.Client(address)

    glfw.init()

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    window = glfw.create_window(256, 256, 'Malt', None, None)
    glfw.make_context_current(window)
    # Don't hide for better OS/Drivers schedule priority
    #glfw.hide_window(window)
    # Minimize instead:
    glfw.iconify_window(window)

    glfw.swap_interval(0)

    pipeline_dir, pipeline_name = os.path.split(pipeline_path)
    if pipeline_dir not in sys.path:
        sys.path.append(pipeline_dir)
    module_name = pipeline_name.split('.')[0]
    module = __import__(module_name)

    pipeline_class = module.PIPELINE
    pipeline = pipeline_class()

    params = pipeline.get_parameters()
    connections['PARAMS'].send(params)

    viewports = {}

    median_time = None

    while glfw.window_should_close(window) == False:

        profiler = cProfile.Profile()
        profiling_data = io.StringIO()
        global PROFILE
        if PROFILE:
            profiler.enable()
        
        start_time = time.perf_counter()

        glfw.poll_events()

        while connections['MATERIAL'].poll():
            msg = connections['MATERIAL'].recv()
            path = msg['path']
            search_paths = msg['search_paths']
            #print('COMPILE MATERIAL :', path)
            material = Bridge.Material.Material(path, pipeline, search_paths)
            connections['MATERIAL'].send(material)
        
        while connections['MESH'].poll():
            msg = connections['MESH'].recv()
            #print('LOAD MESH', msg['name'])
            load_mesh(msg)
        
        while connections['TEXTURE'].poll():
            msg = connections['TEXTURE'].recv()
            try:
                name = msg['name']
                resolution = msg['resolution']
                channels = msg['channels']
                buffer_name = msg['buffer_name']
                sRGB = msg['sRGB']
                w,h = resolution
                size = w*h*channels
                buffer = ipc.SharedMemoryRef(buffer_name, size*ctypes.sizeof(ctypes.c_float))
                float_buffer = (ctypes.c_float*size).from_address(buffer.c.data)
                #print('LOAD TEXTURE', name)
                load_texture(name, resolution, channels, float_buffer, sRGB)
            except:
                import traceback
                #print(traceback.format_exc())
                pass
            connections['TEXTURE'].send('COMPLETE')
        
        while connections['GRADIENT'].poll():
            msg = connections['GRADIENT'].recv()
            name = msg['name']
            pixels = msg['pixels']
            nearest = msg['nearest']
            #print('LOAD GRADIENT', name)
            load_gradient(name, pixels, nearest)
        
        setup_viewports = {}
        while connections['RENDER'].poll():
            #print('SETUP RENDER')
            msg = connections['RENDER'].recv()
            setup_viewports[msg['viewport_id']] = msg

        for msg in setup_viewports.values():
            viewport_id = msg['viewport_id']
            resolution = msg['resolution']
            scene = msg['scene']
            scene_update = msg['scene_update']
            buffer_name = msg['buffer_name']
            w,h = resolution
            buffer = ipc.SharedMemoryRef(buffer_name, w*h*4*4)

            if viewport_id not in viewports:
                viewports[viewport_id] = Viewport(pipeline_class())

            viewports[viewport_id].setup(buffer, resolution, scene, scene_update)
            shared_dic[(viewport_id, 'FINISHED')] = False
        
        active_viewports = False
        for v_id, v in viewports.items():
            #print('RENDER', v_id)
            need_more_samples = v.render()
            if need_more_samples == False and shared_dic[(v_id, 'FINISHED')] == False:
                shared_dic[(v_id, 'FINISHED')] = True
            active_viewports = active_viewports or need_more_samples
        
        if not active_viewports:
            glfw.swap_interval(1)
        else:
            glfw.swap_interval(0)
        glfw.swap_buffers(window)

        if active_viewports:
            t = time.perf_counter() - start_time
            if median_time is None:
                median_time = t
            def lerp(a, b, f):
                return a * (1 - f) + b * f
            median_time = lerp(median_time, t, 0.1)
            #print('FRAME TIME:', t,'SMOOTH:',median_time)
        
        if PROFILE:
            profiler.disable()
            stats = pstats.Stats(profiler, stream=profiling_data)
            stats.strip_dirs()
            stats.sort_stats(pstats.SortKey.CUMULATIVE)
            stats.print_stats()
            if active_viewports:
                #print('PROFILE BEGIN--------------------------------------')
                #print(profiling_data.getvalue())
                #print('PROFILE END--------------------------------------')
                pass

    glfw.terminate()
