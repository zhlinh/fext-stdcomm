//
// StdCommJni.java
// jni
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

package com.mojeter.fndyext.stdcomm.jni;

public class StdCommJni {
    static {
        try {
            System.loadLibrary("c++_shared");
            System.loadLibrary("libstdcomm");
        } catch (Throwable e) {
            e.printStackTrace();
        }
    }

    public static native void setDebugLog(boolean isDebugLog);
}
