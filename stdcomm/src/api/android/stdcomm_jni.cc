//
// stdcomm_jni.cpp
// api/android
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#ifdef __ANDROID__

#  include "stdcomm/api/android/stdcomm_jni.h"
#  include "stdcomm/api/native/stdcomm.h"

#  include <cstdint>
#  include <memory>

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM *vm, void *reserved) {
  (void)reserved;

  return JNI_VERSION_1_6;
}

JNIEXPORT void JNICALL STDCOMM_JNI_API_DEF(setDebugLog)(JNIEnv *env, jclass cls, jboolean is_debug_log) {
  (void)env;
  (void)cls;
  stdcomm_SetDebugLog(is_debug_log);
}

#endif  // __ANDROID__
