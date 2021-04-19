/* Minimal main program -- everything is loaded from the library */

#include "Python.h"

#ifdef MS_WINDOWS
int
typedef unsigned long DWORD;
_declspec(dllexport) DWORD NvOptimusEnablement = 0x00000001;
_declspec(dllexport) int AmdPowerXpressRequestHighPerformance = 0x00000001;
wmain(int argc, wchar_t **argv)
{
	printf("Python GPU\n");
    return Py_Main(argc, argv);
}
#else
int
main(int argc, char **argv)
{
    return _Py_UnixMain(argc, argv);
}
#endif
