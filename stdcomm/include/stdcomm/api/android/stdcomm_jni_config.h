//
// stdcomm_jni_config.h
// api/android
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#ifndef STDCOMM_API_ANDROID_STDCOMM_JNI_CONFIG_H_
#define STDCOMM_API_ANDROID_STDCOMM_JNI_CONFIG_H_

#ifdef __ANDROID__

#  ifndef STDCOMM_JNI_API_PREFIX
#    define STDCOMM_JNI_API_PREFIX Java_com_mojeter_fext_stdcomm_jni_StdCommJni_
#  endif

// the following two macros are utility macros to concatenate two macros
#  define _TOOLS_CONCAT(a, b) a##b
#  define TOOLS_CONCAT(a, b) _TOOLS_CONCAT(a, b)

#  define STDCOMM_JNI_API_DEF(f) TOOLS_CONCAT(STDCOMM_JNI_API_PREFIX, f)

#endif  // __ANDROID__

#endif  // STDCOMM_API_ANDROID_STDCOMM_JNI_CONFIG_H_
