// Copyright (c) 2020 BlenderNPR and contributors. MIT license.

#ifdef _WIN32
#define EXPORT __declspec( dllexport )
#else
#define EXPORT __attribute__ ((visibility ("default")))
#endif

#define IPC_IMPLEMENTATION
#include "ipc.h"

EXPORT ipc_sharedmemory create_shared_memory(char* name, size_t size)
{
    ipc_sharedmemory mem = {0};
    ipc_mem_init(&mem, name, size);
    ipc_mem_create(&mem);

    return mem;
}

EXPORT ipc_sharedmemory open_shared_memory(char* name, size_t size)
{
    ipc_sharedmemory mem = {0};
    ipc_mem_init(&mem, name, size);
    ipc_mem_open_existing(&mem);
    
    return mem;
}

EXPORT void close_shared_memory(ipc_sharedmemory  mem, bool release)
{
    ipc_mem_close(&mem, release);
}


