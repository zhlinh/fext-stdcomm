//
// StdComm.java
// wrapper
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserve.

package com.mojeter.fndyext.stdcomm.wrapper;

import com.mojeter.fndyext.stdcomm.jni.StdCommJni;

/*!
 * \if ZH-CN
 * \file StdComm.java
 * \brief stdcomm通用库java接口文件
 * \else
 * \file StdComm.java
 * \brief stdcomm common library java api file
 * \endif
 */

/*! \addtogroup Android
 * \if ZH-CN
 * StdComm-Android平台
 * \else
 * StdComm for Android Platform
 * \endif
 *  @{
 */

/**
 * \if ZH-CN
 * \brief 通用库java接口类
 *
 * @author ccgo
 * \else
 * \brief stdcomm common java api class.
 *
 * @author ccgo
 * \endif
 */
public class StdComm {
    // -----------------------------------------------------------------------------
    //!  \name stdcomm-base
    //!  @{
    // -----------------------------------------------------------------------------
    static {
        System.loadLibrary("c++_shared");
    }

    /**
     * \if ZH-CN
     * \brief 设置debug log
     *
     * @param isDebugLog 是否打印日志
     * \else
     * \brief set debug log.
     *
     * @param isDebugLog the debug log
     * \endif
     */
    public static void setDebugLog(boolean isDebugLog) {
        StdCommJni.setDebugLog(isDebugLog);
    }

    // -----------------------------------------------------------------------------
    // endregion
    //!  @}  // end name stdcomm-base
    // -----------------------------------------------------------------------------
}

/*! @} */
// end group Android
