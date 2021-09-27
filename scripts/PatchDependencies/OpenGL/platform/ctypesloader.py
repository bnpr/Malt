"""ctypes abstraction layer

We keep rewriting functions as the main entry points change,
so let's just localise the changes here...
"""
import ctypes, logging, os, sys
_log = logging.getLogger( 'OpenGL.platform.ctypesloader' )
#_log.setLevel( logging.DEBUG )
ctypes_version = [
    int(x) for x in ctypes.__version__.split('.')
]
from ctypes import util
import OpenGL

DLL_DIRECTORY = os.path.join( os.path.dirname( OpenGL.__file__ ), 'DLLS' )

def loadLibrary( dllType, name, mode = ctypes.RTLD_GLOBAL ):
    """Load a given library by name with the given mode
    
    dllType -- the standard ctypes pointer to a dll type, such as
        ctypes.cdll or ctypes.windll or the underlying ctypes.CDLL or 
        ctypes.WinDLL classes.
    name -- a short module name, e.g. 'GL' or 'GLU'
    mode -- ctypes.RTLD_GLOBAL or ctypes.RTLD_LOCAL,
        controls whether the module resolves names via other
        modules already loaded into this process.  GL modules
        generally need to be loaded with GLOBAL flags
    
    returns the ctypes C-module object
    """
    if isinstance( dllType, ctypes.LibraryLoader ):
        dllType = dllType._dlltype
    if sys.platform.startswith('linux'):
        return _loadLibraryPosix(dllType, name, mode)
    else:
        return _loadLibraryWindows(dllType, name, mode)


def _loadLibraryPosix(dllType, name, mode):
    """Load a given library for posix systems

    The problem with util.find_library is that it does not respect linker runtime variables like
    LD_LIBRARY_PATH.

    Also we cannot rely on libGLU.so to be available, for example. Most of Linux distributions will
    ship only libGLU.so.1 by default. Files ending with .so are normally used when compiling and are
    provided by dev packages.

    returns the ctypes C-module object
    """
    prefix = 'lib'
    suffix = '.so'
    base_name = prefix + name + suffix
    
    filenames_to_try = []
    # If a .so is missing, let's try libs with so version (e.g libGLU.so.9, libGLU.so.8 and so on)
    filenames_to_try.extend(list(reversed([
        base_name + '.%i' % i for i in range(0, 10)
    ])))
    err = None

    for filename in filenames_to_try:
        try:
            result = dllType(filename, mode)
            _log.debug( 'Loaded %s => %s %s', base_name, filename, result)
            return result
        except Exception as current_err:
            err = current_err
    
    _log.info('''Failed to load library ( %r ): %s''', filename, err or 'No filenames available to guess?')

def _loadLibraryWindows(dllType, name, mode):
    """Load a given library for Windows systems

    returns the ctypes C-module object
    """
    fullName = None
    try:
        if name in ["OpenGL", "GLUT"] and sys.platform == 'darwin' and int(os.uname()[2].split('.')[0]) > 19:
            fullName = "/System/Library/Frameworks/" + name  + ".framework/" + name
        else:
            fullName = util.find_library( name )
        if fullName is not None:
            name = fullName
        elif os.path.isfile( os.path.join( DLL_DIRECTORY, name + '.dll' )):
            name = os.path.join( DLL_DIRECTORY, name + '.dll' )
    except Exception as err:
        _log.info( '''Failed on util.find_library( %r ): %s''', name, err )
        # Should the call fail, we just try to load the base filename...
        pass
    try:
        return dllType( name, mode )
    except Exception as err:
        err.args += (name,fullName)
        raise

def buildFunction( functionType, name, dll ):
    """Abstract away the ctypes function-creation operation"""
    return functionType( (name, dll), )
