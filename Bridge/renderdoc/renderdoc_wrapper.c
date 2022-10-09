#include "renderdoc_app.h"
#include <stddef.h>

#ifdef _WIN32
#define EXPORT __declspec( dllexport )
#else
#define EXPORT __attribute__ ((visibility ("default")))
#endif

RENDERDOC_API_1_4_1* API = NULL;

#ifdef _WIN32
#include <Windows.h>
void init()
{
    if (API) return;
    HMODULE module = GetModuleHandleA("renderdoc.dll");
    if (module)
    {
        pRENDERDOC_GetAPI RENDERDOC_GetAPI = (pRENDERDOC_GetAPI)GetProcAddress(module, "RENDERDOC_GetAPI");
        int result = RENDERDOC_GetAPI(eRENDERDOC_API_Version_1_4_1, (void **)&API);
        if (result != 1) API = NULL;
    }
}
#else
#include <dlfcn.h>
void init()
{
    if (API) return;
    void* module = dlopen("librenderdoc.so", RTLD_NOW | RTLD_NOLOAD);
    if (module)
    {
        pRENDERDOC_GetAPI RENDERDOC_GetAPI = (pRENDERDOC_GetAPI)dlsym(module, "RENDERDOC_GetAPI");
        int result = RENDERDOC_GetAPI(eRENDERDOC_API_Version_1_4_1, (void **)&API);
        if (result != 1) API = NULL;
    }
}
#endif

EXPORT void capture_start()
{
    init();
    if (API) API->StartFrameCapture(NULL, NULL);
}

EXPORT void capture_end()
{
    init();
    if (API) API->EndFrameCapture(NULL, NULL);
}
