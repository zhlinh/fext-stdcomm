//
// stdcomm.h
// api/native
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#ifndef STDCOMM_API_NATIVE_STDCOMM_H_
#define STDCOMM_API_NATIVE_STDCOMM_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifndef COMM_PUBLIC
// this is for non-project use, no need to define COMM_PUBLIC
// or windows will add __imp_ prefix when searching for symbols
#  if defined(COMM_ENABLE_EXPORTS) && COMM_ENABLE_EXPORTS == 1
#    if defined _WIN32 || defined __CYGWIN__
#      ifdef BUILDING_DLL
#        ifdef __GNUC__
#          define COMM_PUBLIC __attribute__((dllexport))
#        else
#          define COMM_PUBLIC __declspec(dllexport)
#        endif
#      else
#        ifdef __GNUC__
#          define COMM_PUBLIC __attribute__((dllimport))
#        else
#          define COMM_PUBLIC __declspec(dllimport)
#        endif
#      endif
#    else
#      if defined(__clang__) || (defined(__GNUC__) && __GNUC__ >= 4)
#        define COMM_PUBLIC __attribute__((visibility("default")))
#      else
#        define COMM_PUBLIC
#      endif
#    endif
#  else
#    define COMM_PUBLIC
#  endif  // defined(COMM_ENABLE_EXPORTS) && COMM_ENABLE_EXPORTS == 1
#endif    // #ifndef (COMM_PUBLIC)

//! \if ZH-CN
//! \brief 设置调试日志
//!
//! \param is_debug_log 是否启用调试日志
//! \else
//! \brief set debug log.
//!
//! \param is_debug_log  the debug log
//! \endif
void stdcomm_SetDebugLog(bool is_debug_log);


#ifdef __cplusplus
}
#endif

#endif  // STDCOMM_API_NATIVE_FOUNDRY_COMM_LOG_H_
