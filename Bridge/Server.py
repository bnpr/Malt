# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

import ctypes, os
import glfw

from Malt.GL import GL
from Malt.GL.GL import *
from Malt.GL.RenderTarget import RenderTarget

import Bridge.Mesh, Bridge.Material, Bridge.Texture
from . import ipc as ipc

import logging as log
def setup_logging(log_path, log_level):
    log.basicConfig(filename=log_path, level=log_level, format='Malt > %(message)s')
    console_logger = log.StreamHandler()
    console_logger.setLevel(log.WARNING)
    log.getLogger().addHandler(console_logger)


def log_system_info():
    import sys, platform
    log.info('SYSTEM INFO')
    log.info('-'*80)
    log.info('PYTHON: {}'.format(sys.version))
    log.info('OS: {}'.format(platform.platform()))
    log.info('CPU: {}'.format(platform.processor()))

    log.info('OPENGL CONTEXT:')
    log.info(glGetString(GL_VENDOR).decode())
    log.info(glGetString(GL_RENDERER).decode())
    log.info(glGetString(GL_VERSION).decode())
    log.info(glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
    for key, value in GL_NAMES.items():
        if key.startswith('GL_MAX'):
            try:
                log.info('{}: {}'.format(key, glGetInteger(value)))
            except:
                pass

    def log_format_prop(format, prop):
        read = glGetInternalformativ(GL_TEXTURE_2D, format, prop, 1)
        log.debug('{} {}: {}'.format(GL_ENUMS[format], GL_ENUMS[prop], GL_ENUMS[read]))

    def log_format_props(format):
        log_format_prop(format, GL_READ_PIXELS)
        log_format_prop(format, GL_READ_PIXELS_FORMAT)
        log_format_prop(format, GL_READ_PIXELS_TYPE)
        log_format_prop(format, GL_TEXTURE_IMAGE_FORMAT)
        log_format_prop(format, GL_TEXTURE_IMAGE_TYPE)

    log_format_props(GL_RGB8)
    log_format_props(GL_RGBA8)
    log_format_props(GL_RGB16F)
    log_format_props(GL_RGBA16F)
    log_format_props(GL_RGB32F)
    log_format_props(GL_RGBA32F)

    log.info('-'*80)

class PBO(object):

    def __init__(self):
        self.handle = gl_buffer(GL_INT, 1)
        self.size = None
        self.sync = None
        self.buffer = None
    
    def __del__(self):
        glDeleteBuffers(1, self.handle)
    
    def setup(self, texture, buffer):
        self.buffer = buffer
        render_target = RenderTarget([texture])
        w,h = texture.resolution
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
        GL.glReadPixels(0, 0, w, h, texture.format, texture.data_format, 0)
        glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

        if self.sync:
            glDeleteSync(self.sync)
        self.sync = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
    
    def poll(self):
        wait = glClientWaitSync(self.sync, GL_SYNC_FLUSH_COMMANDS_BIT, 0)
        return wait == GL_ALREADY_SIGNALED
    
    def load(self):
        wait = glClientWaitSync(self.sync, GL_SYNC_FLUSH_COMMANDS_BIT, 0)
        if wait == GL_ALREADY_SIGNALED:
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.handle[0])
            result = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)
            if result:
                ctypes.memmove(self.buffer.c.data, result, self.size)
                glUnmapBuffer(GL_PIXEL_PACK_BUFFER)
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
            return True
        return False


class Viewport(object):

    def __init__(self, pipeline, is_final_render):
        self.pipeline = pipeline
        self.buffers = None
        self.resolution = None
        self.read_resolution = None
        self.scene = None
        self.pbos_active = []
        self.pbos_inactive = []
        self.is_new_frame = True
        self.needs_more_samples = True
        self.is_final_render = is_final_render
    
    def setup(self, buffers, resolution, scene, scene_update):
        if self.resolution != resolution:
            self.pbos_inactive.extend(self.pbos_active)
            self.pbos_active = []
        
        self.buffers = buffers
        self.resolution = resolution

        self.sample_index = 0
        self.is_new_frame = True
        self.needs_more_samples = True
        
        if scene_update or self.scene is None:
            for mesh in scene.meshes:
                if mesh is None:
                    continue
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
            import time
            start_time = time.perf_counter()
            result = self.pipeline.render(self.resolution, self.scene, self.is_final_render, self.is_new_frame)
            log.debug('RENDER TIME: {} RESOLUTION: {}'.format(time.perf_counter() - start_time, self.resolution))
            self.is_new_frame = False
            self.needs_more_samples = self.pipeline.needs_more_samples()
            
            pbos = None
            
            if len(self.pbos_inactive) > 0:
                pbos = self.pbos_inactive.pop()
            else:
                pbos = {}
            
            for key, texture in result.items():
                if texture and key in self.buffers.keys():
                    if key not in pbos.keys():
                        pbos[key] = PBO()
                    pbos[key].setup(texture, self.buffers[key])
            
            self.pbos_active.append(pbos)

        if len(self.pbos_active) > 0:
            for i, pbos in reversed(list(enumerate(self.pbos_active))):
                is_ready = True
                for pbo in pbos.values():
                    if pbo.poll() == False:
                        is_ready = False
                if is_ready:
                    for pbo in pbos.values():
                        pbo.load()
                        self.pbos_inactive.extend(self.pbos_active[:i+1])
                        self.pbos_active = self.pbos_active[i+1:]
                        self.read_resolution = self.resolution
                    break
            log.debug('{} PBOs active'.format(len(self.pbos_active)))
        
        return self.needs_more_samples or len(self.pbos_active) > 0

import os, sys, time
import cProfile, pstats, io
import multiprocessing.connection as connection

PROFILE = False

def main(pipeline_path, connection_addresses, shared_dic, log_path, debug_mode):
    log_level = log.DEBUG if debug_mode else log.INFO
    setup_logging(log_path, log_level)
    log.info('DEBUG MODE: {}'.format(debug_mode))

    # Trying to change process prioriy in Linux seems to hang Malt for some users
    if sys.platform == 'win32':
        import psutil
        psutil.Process().nice(psutil.REALTIME_PRIORITY_CLASS)

    log.info('CONNECTIONS:')
    connections = {}
    for name, address in connection_addresses.items():
        log.info('Name: {} Adress: {}'.format(name, address))
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

    log_system_info()
    
    log.info('INIT PIPELINE: ' + pipeline_path)

    pipeline_dir, pipeline_name = os.path.split(pipeline_path)
    if pipeline_dir not in sys.path:
        sys.path.append(pipeline_dir)
    module_name = pipeline_name.split('.')[0]
    module = __import__(module_name)

    pipeline_class = module.PIPELINE
    pipeline_class.SHADER_INCLUDE_PATHS.append(pipeline_dir)
    pipeline = pipeline_class()

    params = pipeline.get_parameters()
    graphs = pipeline.get_graphs()
    connections['PARAMS'].send((params, graphs))

    viewports = {}

    while glfw.window_should_close(window) == False:
        
        try:
            profiler = cProfile.Profile()
            profiling_data = io.StringIO()
            global PROFILE
            if PROFILE:
                profiler.enable()
            
            start_time = time.perf_counter()

            glfw.poll_events()

            while connections['MATERIAL'].poll():
                msg = connections['MATERIAL'].recv()
                log.debug('COMPILE MATERIAL : {}'.format(msg))
                path = msg['path']
                search_paths = msg['search_paths']
                material = Bridge.Material.Material(path, pipeline, search_paths)
                connections['MATERIAL'].send(material)
            
            while connections['SHADER REFLECTION'].poll():
                msg = connections['SHADER REFLECTION'].recv()
                log.debug('REFLECT SHADER : {}'.format(msg))
                paths = msg['paths']
                results = {}
                from Malt.GL.Shader import GLSL_Reflection, shader_preprocessor
                for path in paths:
                    src = shader_preprocessor(open(path).read(), [os.path.dirname(path)])
                    reflection = {
                        'structs':  GLSL_Reflection.reflect_structs(src),
                        'functions':  GLSL_Reflection.reflect_functions(src),
                        'paths': set([path])
                    }
                    for struct in reflection['structs'].values(): reflection['paths'].add(struct['file'])
                    for function in reflection['functions'].values(): reflection['paths'].add(function['file'])
                    results[path] = reflection
                connections['SHADER REFLECTION'].send(results)
            
            while connections['MESH'].poll():
                msg = connections['MESH'].recv()
                log.debug('LOAD MESH : {}'.format(msg))
                Bridge.Mesh.load_mesh(msg)
            
            while connections['TEXTURE'].poll():
                msg = connections['TEXTURE'].recv()
                log.debug('LOAD TEXTURE : {}'.format(msg))
                name = msg['name']
                resolution = msg['resolution']
                channels = msg['channels']
                buffer_name = msg['buffer_name']
                sRGB = msg['sRGB']
                w,h = resolution
                size = w*h*channels
                buffer = ipc.SharedMemoryRef(buffer_name, size*ctypes.sizeof(ctypes.c_float))
                float_buffer = (ctypes.c_float*size).from_address(buffer.c.data)
                Bridge.Texture.load_texture(name, resolution, channels, float_buffer, sRGB)
                connections['TEXTURE'].send('COMPLETE')
            
            while connections['GRADIENT'].poll():
                msg = connections['GRADIENT'].recv()
                log.debug('LOAD GRADIENT : {}'.format(msg))
                name = msg['name']
                pixels = msg['pixels']
                nearest = msg['nearest']
                Bridge.Texture.load_gradient(name, pixels, nearest)
            
            #TODO: Bad workaround to make sure the scene assets are loaded
            if connections['RENDER'].poll():
                needs_loading = False
                for key in ['MATERIAL','MESH','TEXTURE','GRADIENT']:
                    if connections[key].poll():
                        needs_loading = True
                if needs_loading:
                    continue
            
            setup_viewports = {}
            while connections['RENDER'].poll():
                msg = connections['RENDER'].recv()
                log.debug('SETUP RENDER : {}'.format(msg))
                setup_viewports[msg['viewport_id']] = msg

            for msg in setup_viewports.values():
                viewport_id = msg['viewport_id']
                resolution = msg['resolution']
                scene = msg['scene']
                scene_update = msg['scene_update']
                buffer_names = msg['buffer_names']
                w,h = resolution
                buffers = {}
                for key, buffer_name in buffer_names.items():
                    if buffer_name:
                        buffers[key] = ipc.SharedMemoryRef(buffer_name, w*h*4*4)

                if viewport_id not in viewports:
                    viewports[viewport_id] = Viewport(pipeline_class(), viewport_id == 0)

                viewports[viewport_id].setup(buffers, resolution, scene, scene_update)
                shared_dic[(viewport_id, 'FINISHED')] = False
            
            active_viewports = False
            for v_id, v in viewports.items():
                need_more_samples = v.render()
                shared_dic[(v_id, 'READ_RESOLUTION')] = v.read_resolution
                if need_more_samples == False and shared_dic[(v_id, 'FINISHED')] == False:
                    shared_dic[(v_id, 'FINISHED')] = True
                active_viewports = active_viewports or need_more_samples
            
            if not active_viewports:
                glfw.swap_interval(1)
            else:
                glfw.swap_interval(0)
            glfw.swap_buffers(window)

            if active_viewports:
                log.debug('FRAME TIME: {} '.format(time.perf_counter() - start_time))
            
            if PROFILE:
                profiler.disable()
                stats = pstats.Stats(profiler, stream=profiling_data)
                stats.strip_dirs()
                stats.sort_stats(pstats.SortKey.CUMULATIVE)
                stats.print_stats()
                if active_viewports:
                    log.debug(profiling_data.getvalue())
        except (ConnectionResetError, EOFError):
            #Connection Lost
            break
        except:
            import traceback
            log.error(traceback.format_exc())

    glfw.terminate()

