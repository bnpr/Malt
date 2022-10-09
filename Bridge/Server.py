import importlib
import os, sys, time, ctypes, os, copy
import cProfile, pstats, io
import multiprocessing.connection as connection

import glfw

from Malt.GL import GL
from Malt.GL.GL import *
from Malt.GL.RenderTarget import RenderTarget
from Malt.GL.Texture import Texture
from Malt.PipelinePlugin import load_plugins_from_dir

import Bridge.Mesh, Bridge.Material, Bridge.Texture
from . import ipc as ipc

from Malt.Utils import LOG
def setup_logging(log_path, log_level):
    LOG.basicConfig(filename=log_path, level=log_level, format='Malt > %(message)s')
    console_logger = LOG.StreamHandler()
    console_logger.setLevel(LOG.WARNING)
    LOG.getLogger().addHandler(console_logger)


def log_system_info():
    import sys, platform
    LOG.info('SYSTEM INFO')
    LOG.info('-'*80)
    LOG.info('PYTHON: {}'.format(sys.version))
    LOG.info('OS: {}'.format(platform.platform()))
    LOG.info('CPU: {}'.format(platform.processor()))

    LOG.info('OPENGL CONTEXT:')
    LOG.info(glGetString(GL_VENDOR).decode())
    LOG.info(glGetString(GL_RENDERER).decode())
    LOG.info(glGetString(GL_VERSION).decode())
    LOG.info(glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
    LOG.info(f"GL_ARB_bindless_texture support : {hasGLExtension('GL_ARB_bindless_texture')}")
    for key, value in GL_NAMES.items():
        if key.startswith('GL_MAX'):
            try:
                LOG.info('{}: {}'.format(key, glGetInteger(value)))
            except:
                pass

    def log_format_prop(format, prop):
        read = glGetInternalformativ(GL_TEXTURE_2D, format, prop, 1)
        try:
            LOG.info('{} {}: {}'.format(GL_ENUMS[format], GL_ENUMS[prop], GL_ENUMS[read]))
        except:
            #Some returned formats are not present in GL_ENUMS? See #393
            import traceback
            traceback.print_exc()

    def log_format_props(format):
        log_format_prop(format, GL_READ_PIXELS)
        log_format_prop(format, GL_READ_PIXELS_FORMAT)
        log_format_prop(format, GL_READ_PIXELS_TYPE)
        log_format_prop(format, GL_TEXTURE_IMAGE_FORMAT)
        log_format_prop(format, GL_TEXTURE_IMAGE_TYPE)

    log_format_props(GL_RGB8)
    log_format_props(GL_RGBA8)
    log_format_props(GL_RGBA)
    log_format_props(GL_SRGB)
    log_format_props(GL_SRGB_ALPHA)
    log_format_props(GL_RGB16F)
    log_format_props(GL_RGBA16F)
    log_format_props(GL_RGB32F)
    log_format_props(GL_RGBA32F)

    LOG.info('-'*80)

class PBO():

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
        size = w * h * texture.channel_count * texture.channel_size
        assert(buffer.size_in_bytes() >= size)
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
                ctypes.memmove(self.buffer.buffer(), result, self.size)
                glUnmapBuffer(GL_PIXEL_PACK_BUFFER)
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
            return True
        return False


class Viewport():

    def __init__(self, pipeline, is_final_render, bit_depth):
        self.pipeline = pipeline
        self.buffers = None
        self.resolution = None
        self.read_resolution = None
        self.scene = None
        self.bit_depth = bit_depth
        self.target_format = None
        self.final_texture = None
        self.final_target = None
        self.pbos_active = []
        self.pbos_inactive = []
        self.is_new_frame = True
        self.needs_more_samples = True
        self.is_final_render = is_final_render
        self.renderdoc_capture = False

        self.stat_max_frame_latency = 0
        self.stat_cpu_frame_time = 0
        self.stat_time_start = 0
        self.stat_render_time = 0
    
    def get_print_stats(self):
        return '\n'.join((
            'Resolution : {}'.format(self.resolution),
            'Sample : {} / {}'.format(self.pipeline.sample_count, len(self.pipeline.get_samples())),
            'Sample Time : {:.3f} ms'.format((self.stat_render_time * 1000) / self.pipeline.sample_count),
            'Total Time : {:.3f} s'.format(self.stat_render_time),
            'Latency : {} frames'.format(len(self.pbos_active)),
            'Max Latency : {} frames'.format(self.stat_max_frame_latency),
        ))
    
    def setup(self, new_buffers, resolution, scene, scene_update, renderdoc_capture):
        if self.resolution != resolution:
            self.resolution = resolution
            self.pbos_inactive.extend(self.pbos_active)
            self.pbos_active = []
            assert(new_buffers is not None)
            if self.bit_depth == 8:
                self.target_format = GL_UNSIGNED_BYTE
                if glGetInternalformativ(GL_TEXTURE_2D, GL_RGBA8, GL_READ_PIXELS, 1) != GL_ZERO:
                    self.target_format = glGetInternalformativ(GL_TEXTURE_2D, GL_RGBA8, GL_TEXTURE_IMAGE_TYPE, 1)
                try:
                    self.final_texture = Texture(resolution, GL_RGBA8, self.target_format, pixel_format=GL_RGBA)
                except:
                    # Fallback to unsigned byte, just in case
                    self.target_format = GL_UNSIGNED_BYTE
                    self.final_texture = Texture(resolution, GL_RGBA8, self.target_format)
                self.final_texture.channel_size = 1
                self.final_target = RenderTarget([self.final_texture])
            else:
                if self.bit_depth == 16:
                    self.target_format = GL_RGBA16F
                elif self.bit_depth == 32:
                    self.target_format = GL_RGBA32F
                self.final_texture = Texture(resolution, self.target_format)
                self.final_target = RenderTarget([self.final_texture])
        
        if new_buffers:
            self.buffers = new_buffers

        self.sample_index = 0
        self.is_new_frame = True
        self.needs_more_samples = True

        self.renderdoc_capture = renderdoc_capture

        self.stat_time_start = time.perf_counter()
        
        if scene_update or self.scene is None:
            for key, proxy in scene.proxys.items():
                proxy.resolve()
            
            for obj in scene.objects:
                obj.matrix = (ctypes.c_float * 16)(*obj.matrix)
            
            scene.batches = self.pipeline.build_scene_batches(scene.objects)
            self.scene = scene
        else:
            self.scene.camera = scene.camera
            self.scene.time = scene.time
            self.scene.frame = scene.frame
    
    TO_SRGB_SHADER = None
    def to_srgb(self, texture, target):
        if Viewport.TO_SRGB_SHADER is None:
            source='#include "Passes/sRGBConversion.glsl"'
            Viewport.TO_SRGB_SHADER = self.pipeline.compile_shader_from_source(source)
        Viewport.TO_SRGB_SHADER.uniforms["to_srgb"].set_value(True)
        Viewport.TO_SRGB_SHADER.textures["input_texture"] = texture
        self.pipeline.draw_screen_pass(Viewport.TO_SRGB_SHADER, target)   
    def ensure_correct_format(self, key, texture):
        format = GL_R32F if key == 'DEPTH' else self.target_format
        if texture.format == format and texture.resolution == self.resolution:
            return texture
        target = self.final_target
        if key != 'COLOR': #Create on the fly, since final render targets can be large
            target = RenderTarget([Texture(self.resolution, format)])
        if self.bit_depth == 8 and key != 'DEPTH':
            self.to_srgb(texture, target)
        else:
            self.pipeline.copy_textures(target, [texture])
        return target.targets[0]
    
    def render(self):
        from . import renderdoc
        if self.renderdoc_capture:
            renderdoc.capture_start()

        if self.needs_more_samples:
            result = self.pipeline.render(self.resolution, self.scene, self.is_final_render, self.is_new_frame)
            self.is_new_frame = False
            self.needs_more_samples = self.pipeline.needs_more_samples()
            if self.is_final_render == False or self.needs_more_samples == False:
                pbos = None
                if len(self.pbos_inactive) > 0:
                    pbos = self.pbos_inactive.pop()
                else:
                    pbos = {}
                for key, texture in result.items():
                    if texture and key in self.buffers.keys():
                        if key not in pbos.keys():
                            pbos[key] = PBO()
                        texture = self.ensure_correct_format(key, texture)
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
            
            self.stat_render_time = time.perf_counter() - self.stat_time_start
            self.stat_max_frame_latency = max(len(self.pbos_active), self.stat_max_frame_latency)
        
        if self.renderdoc_capture:
            renderdoc.capture_end()
            self.renderdoc_capture = False
        
        return self.needs_more_samples == False and len(self.pbos_active) == 0


PROFILE = False

def main(pipeline_path, viewport_bit_depth, connection_addresses,
    shared_dic, lock, log_path, debug_mode, plugins_paths, docs_path):
    log_level = LOG.DEBUG if debug_mode else LOG.INFO
    setup_logging(log_path, log_level)
    LOG.info('DEBUG MODE: {}'.format(debug_mode))

    LOG.info('CONNECTIONS:')
    connections = {}
    for name, address in connection_addresses.items():
        LOG.info('Name: {} Adress: {}'.format(name, address))
        connections[name] = connection.Client(address)
    
    glfw.ERROR_REPORTING = True
    glfw.init()

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    window = glfw.create_window(256, 256, 'Malt', None, None)
    glfw.make_context_current(window)
    # Don't hide for better OS/Drivers schedule priority
    #glfw.hide_window(window)
    # Minimize instead:
    glfw.iconify_window(window)

    glfw.swap_interval(0)

    log_system_info()
    
    LOG.info('INIT PIPELINE: ' + pipeline_path)

    try:
        pipeline_dir, pipeline_name = os.path.split(pipeline_path)
        if pipeline_dir not in sys.path:
            sys.path.append(pipeline_dir)
        module_name = pipeline_name.split('.')[0]
        module = __import__(module_name)

        pipeline_class = module.PIPELINE
        pipeline_class.SHADER_INCLUDE_PATHS.append(pipeline_dir)
        
        if docs_path: #build docs before loading plugins
            from . import Docs
            try:
                Docs.build_docs(pipeline_class(), docs_path)
            except:
                import traceback
                traceback.print_exc()
        
        plugins = []
        for dir in plugins_paths:
            plugins += load_plugins_from_dir(dir)
        pipeline = pipeline_class(plugins)

        params = pipeline.get_parameters()
        graphs = pipeline.get_graphs()
        outputs = pipeline.get_render_outputs()
        connections['MAIN'].send({
            'msg_type': 'PARAMS',
            'params': params,
            'graphs': graphs,
            'outputs': outputs
        })
    except:
        import traceback
        exception = traceback.format_exc()
        LOG.error(exception)

        from Malt import PipelineParameters
        
        connections['MAIN'].send({
            'msg_type': 'PARAMS',
            'params': PipelineParameters.PipelineParameters(),
            'graphs': {},
            'outputs': {}
        })

    viewports = {}
    last_exception = ''
    repeated_exception = 0

    while glfw.window_should_close(window) == False:
        
        try:
            profiler = cProfile.Profile()
            profiling_data = io.StringIO()
            global PROFILE
            if PROFILE:
                profiler.enable()
            
            start_time = time.perf_counter()

            glfw.poll_events()

            while connections['REFLECTION'].poll():
                msg = connections['REFLECTION'].recv()
                if msg['msg_type'] == 'SHADER REFLECTION':
                    LOG.debug('REFLECT SHADER : {}'.format(msg))
                    paths = msg['paths']
                    results = {}
                    from Malt.GL.Shader import glsl_reflection, shader_preprocessor
                    for path in paths:
                        try:
                            root_path = os.path.dirname(path)
                            src = '#include "{}"\n'.format(path)
                            src = shader_preprocessor(src, [root_path])
                            reflection = glsl_reflection(src, root_path)
                            reflection['paths'] = set([path])
                            for struct in reflection['structs'].values(): reflection['paths'].add(struct['file'])
                            for function in reflection['functions'].values(): reflection['paths'].add(function['file'])
                            results[path] = reflection
                        except:
                            results[path] = {
                                'structs':{},
                                'functions':{},
                                'paths':[],
                            }
                            import traceback
                            LOG.error(traceback.format_exc())
                    connections['REFLECTION'].send(results)
                if msg['msg_type'] == 'GRAPH RELOAD':
                    graph_types = msg['graph_types']
                    for type in graph_types:
                        pipeline.graphs[type].setup_reflection()
                    for viewport in viewports.values():
                        viewport.pipeline.graphs = pipeline.graphs
                    graphs = pipeline.get_graphs()
                    connections['REFLECTION'].send(graphs)

            while connections['MAIN'].poll():
                msg = connections['MAIN'].recv()
                
                if msg['msg_type'] == 'MATERIAL':
                    LOG.debug('COMPILE MATERIAL : {}'.format(msg))
                    path = msg['path']
                    search_paths = msg['search_paths']
                    custom_passes = msg['custom_passes']
                    material = Bridge.Material.Material(path, pipeline, search_paths, custom_passes)
                    connections['MAIN'].send({
                        'msg_type': 'MATERIAL',
                        'material' : material
                    })
                
                if msg['msg_type'] == 'MESH':
                    msg_log = copy.copy(msg)
                    msg_log['data'] = None
                    LOG.debug('LOAD MESH : {}'.format(msg_log))
                    Bridge.Mesh.load_mesh(pipeline, msg)
                
                if msg['msg_type'] == 'TEXTURE':
                    LOG.debug('LOAD TEXTURE : {}'.format(msg))
                    Bridge.Texture.load_texture(msg)
                
                if msg['msg_type'] == 'GRADIENT':
                    msg_log = copy.copy(msg)
                    msg_log['pixels'] = None
                    LOG.debug('LOAD GRADIENT : {}'.format(msg_log))
                    name = msg['name']
                    pixels = msg['pixels']
                    nearest = msg['nearest']
                    Bridge.Texture.load_gradient(name, pixels, nearest)
                
                if msg['msg_type'] == 'RENDER':
                    LOG.debug('SETUP RENDER : {}'.format(msg))
                    viewport_id = msg['viewport_id']
                    resolution = msg['resolution']
                    scene = msg['scene']
                    scene_update = msg['scene_update']
                    new_buffers = msg['new_buffers']
                    renderdoc_capture = msg['renderdoc_capture']

                    if viewport_id not in viewports:
                        bit_depth = viewport_bit_depth if viewport_id != 0 else 32
                        viewports[viewport_id] = Viewport(pipeline_class(plugins), viewport_id == 0, bit_depth)

                    viewports[viewport_id].setup(new_buffers, resolution, scene, scene_update, renderdoc_capture)
                    shared_dic[(viewport_id, 'FINISHED')] = False
                    shared_dic[(viewport_id, 'SETUP')] = True
            
            active_viewports = {}
            render_finished = True
            for v_id, v in viewports.items():
                if v.needs_more_samples:
                    active_viewports[v_id] = v
                has_finished = v.render()
                if has_finished == False:
                    render_finished = False
                shared_dic[(v_id, 'READ_RESOLUTION')] = v.read_resolution
                if has_finished and shared_dic[(v_id, 'FINISHED')] == False:
                    shared_dic[(v_id, 'FINISHED')] = True
            
            if render_finished:
                glfw.swap_interval(1)
            else:
                glfw.swap_interval(0)
            glfw.swap_buffers(window)

            if len(active_viewports) > 0:
                stats = ''
                for v_id, v in active_viewports.items():
                    stats += "Viewport ({}):\n{}\n\n".format(v_id, v.get_print_stats())
                shared_dic['STATS'] = stats
                LOG.debug('STATS: {} '.format(stats))
            
            if PROFILE:
                profiler.disable()
                stats = pstats.Stats(profiler, stream=profiling_data)
                stats.strip_dirs()
                stats.sort_stats(pstats.SortKey.CUMULATIVE)
                stats.print_stats()
                if active_viewports:
                    LOG.debug(profiling_data.getvalue())
        except (ConnectionResetError, EOFError):
            #Connection Lost
            break
        except:
            import traceback
            exception = traceback.format_exc()
            if exception != last_exception:
                LOG.error(exception)
                repeated_exception = 0
                last_exception = exception
            else:
                if repeated_exception in (1,10,100,1000,10000,100000):
                    LOG.error('(Repeated {}+ times)'.format(repeated_exception))
                repeated_exception += 1

    glfw.terminate()
