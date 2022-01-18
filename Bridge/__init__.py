def reload():
    import importlib
    from . import Client_API, Server, Material, Mesh, Texture
    for module in [ Client_API, Server, Material, Mesh, Texture ]:
        importlib.reload(module)

def start_server(pipeline_path, viewport_bit_depth, connection_addresses, 
    shared_dic, lock, log_path, debug_mode, renderdoc_path, plugins_paths):
    import os, sys
    # Trying to change process prioriy in Linux seems to hang Malt for some users
    if sys.platform == 'win32':
        import psutil
        psutil.Process().nice(psutil.REALTIME_PRIORITY_CLASS)
    if renderdoc_path and os.path.exists(renderdoc_path):
        import subprocess
        subprocess.call([renderdoc_path, 'inject', '--PID={}'.format(os.getpid())])

    from . import Server
    try:
        Server.main(pipeline_path, viewport_bit_depth, connection_addresses,
            shared_dic, lock, log_path, debug_mode, plugins_paths)
    except:
        import traceback, logging as LOG
        LOG.error(traceback.format_exc())
