def get_modules():
    from . import MaltNode, MaltNodeTree, MaltNodeUITools, MaltSocket, MaltCustomPasses
    modules = [MaltNode, MaltNodeTree, MaltNodeUITools, MaltSocket, MaltCustomPasses]
    
    import importlib, os
    nodes_dir = os.path.join(os.path.dirname(__file__), 'Nodes')
    for name in os.listdir(nodes_dir):
        try:
            if name == '__pycache__':
                continue
            if name.endswith('.py'):
                name = name[:-3]
            module = importlib.import_module(f'BlenderMalt.MaltNodes.Nodes.{name}')
            modules.append(module)
        except ModuleNotFoundError:
            # Ignore it. The file or dir is not a python module
            pass
        except Exception:
            import traceback
            traceback.print_exc()
    
    return modules
    

def register():
    import importlib
    for module in get_modules():
        importlib.reload(module)

    for module in get_modules():
        module.register()

def unregister():
    for module in reversed(get_modules()):
        module.unregister()

        