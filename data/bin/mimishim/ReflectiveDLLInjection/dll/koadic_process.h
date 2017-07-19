#pragma once

#include <Windows.h>

#include "koadic_types.h"

BOOL koadic_create_sysnative_process(LPCSTR program, LPDWORD dwPID);
BOOL koadic_fork_x64(koadic_shim_parsed *parsed, LPWSTR lpParam, char *data, DWORD dwDataSize);