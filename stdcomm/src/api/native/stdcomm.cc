//
// stdcomm.cc
// api/native
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#include "stdcomm/api/native/stdcomm.h"

#include "stdcomm/base/global_var.h"

void stdcomm_SetDebugLog(bool is_debug_log) { 
    stdcomm::GlobalVar::GetInstance().debug_ = is_debug_log;
}

