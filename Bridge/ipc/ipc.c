// Copyright (c) 2020-2021 BNPR, Miguel Pozo and contributors. MIT license.

#ifdef _WIN32
#define EXPORT __declspec( dllexport )
#else
#define EXPORT __attribute__ ((visibility ("default")))
#endif

#define IPC_IMPLEMENTATION
#include "ipc.h"

EXPORT int create_shared_memory(char* name, size_t size, ipc_sharedmemory* mem)
{
    ipc_mem_init(mem, name, size);
    if (ipc_mem_create(mem) != 0) {
        return errno;
    }
    return 0;
}

EXPORT int open_shared_memory(char* name, size_t size, ipc_sharedmemory* mem)
{
    ipc_mem_init(mem, name, size);
    if (ipc_mem_open_existing(mem) != 0) {
        return errno;
    }
    return 0;
}

EXPORT void close_shared_memory(ipc_sharedmemory  mem, bool release)
{
    ipc_mem_close(&mem, release);
}
