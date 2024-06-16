//
// stdcomm_jni.h
// api/android
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#ifndef STDCOMM_API_ANDROID_STDCOMM_JNI_H_
#define STDCOMM_API_ANDROID_STDCOMM_JNI_H_

#ifdef __ANDROID__

#  include <jni.h>

#  include <string>
#
#  include "stdcomm/api/android/stdcomm_jni_config.h"

#  ifdef __cplusplus
extern "C" {
#  endif

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved);

JNIEXPORT void JNICALL STDCOMM_JNI_API_DEF(setDebugLog)(JNIEnv *env, jclass cls, jboolean is_debug_log);


#  ifdef __cplusplus
}
#  endif

#endif  // __ANDROID__

#endif  // STDCOMM_API_ANDROID_STDCOMM_JNI_H_
