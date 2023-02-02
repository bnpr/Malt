def reload():
    import importlib
    from . import Client_API, Server, Material, Mesh, Texture
    for module in [ Client_API, Server, Material, Mesh, Texture ]:
        importlib.reload(module)

def start_server(pipeline_path, viewport_bit_depth, connection_addresses, 
    shared_dic, lock, log_path, debug_mode, renderdoc_path, plugins_paths, docs_path):
    import logging
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(filename=log_path, level=log_level, format='Malt > %(message)s')
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.WARNING)
    logging.getLogger().addHandler(console_logger)
    
    import os, sys, ctypes
    if sys.platform == 'win32':
        win = ctypes.windll.kernel32
        HIGH_PRIORITY_CLASS = 0x00000080
        PROCESS_SET_INFORMATION = 0x0200
        process = win.OpenProcess(PROCESS_SET_INFORMATION, 0, win.GetCurrentProcessId())
        win.SetPriorityClass(process, HIGH_PRIORITY_CLASS)
        win.CloseHandle(process)
    if renderdoc_path and os.path.exists(renderdoc_path):
        import subprocess
        subprocess.call([renderdoc_path, 'inject', '--PID={}'.format(os.getpid())])

    from . import Server
    try:
        Server.main(pipeline_path, viewport_bit_depth, connection_addresses,
            shared_dic, lock, log_path, debug_mode, plugins_paths, docs_path)
    except:
        import traceback
        logging.error(traceback.format_exc())
