//
// Copyright 2024 zhlinh and ccgo Project Authors. All rights reserved.
// Use of this source code is governed by a MIT-style
// license that can be found at
//
// https://opensource.org/license/MIT
//
// The above copyright notice and this permission
// notice shall be included in all copies or
// substantial portions of the Software.

package com.ccgo.gradle.buildlogic.common

import org.gradle.api.GradleException
import org.gradle.api.provider.Provider
import org.gradle.process.ExecResult

internal fun execCommand(cmd: String): String {
    // kotlin run command and get output
    val process = Runtime.getRuntime().exec(cmd)
    process.waitFor()
    val output = process.inputStream.bufferedReader().readText()
    return output.trim()
}

internal fun checkExecResult(resultToCheck: Provider<ExecResult>?) {
    if (resultToCheck != null && resultToCheck.isPresent()) {
        if (resultToCheck.get().getExitValue() != 0) {
            throw GradleException("checkExecResult Non-zero exit value: " + resultToCheck.get().getExitValue())
        }
    } else {
        throw GradleException("checkExecResult Returned a null execResult object")
    }
    println("checkExecResult success")
}
