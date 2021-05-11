# Copyright (c) 2020 BlenderNPR and contributors. MIT license. 

def reload():
    import importlib
    from . import Client_API, Server, Material, Mesh, Texture
    for module in [ Client_API, Server, Material, Mesh, Texture ]:
        importlib.reload(module)

def start_server(pipeline_path, connection_addresses, shared_dic, log_path, debug_mode):
    import os, sys
    # Trying to change process prioriy in Linux seems to hang Malt for some users
    if sys.platform == 'win32':
        import psutil
        psutil.Process().nice(psutil.REALTIME_PRIORITY_CLASS)
        import subprocess
        subprocess.call(["C:\\Program Files\RenderDoc\\renderdoccmd.exe", 'inject', '--PID={}'.format(os.getpid())])
        import time
        time.sleep(0.5)

    from . import Server
    Server.main(pipeline_path, connection_addresses, shared_dic, log_path, debug_mode)
