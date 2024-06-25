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

package com.ccgo.gradle.buildlogic.common.utils

internal fun getGpgKeyFromKeyId(keyId: String, keyPass: String): String {
    val keyPassItem = if (keyPass.isEmpty()) "" else "--passphrase $keyPass"
    val result = execCommand("gpg --batch --pinentry-mode=loopback $keyPassItem" +
            " --export-secret-keys --armor $keyId")
    return normalizeGpgKey(result)
}

internal fun getGpgKeyFromKeyRingFile(keyRingFile: String, keyPass: String): String {
    val keyPassItem = if (keyPass.isEmpty()) "" else "--passphrase $keyPass"
    val result = execCommand("gpg --batch --pinentry-mode=loopback $keyPassItem" +
            " --no-default-keyring --secret-keyring $keyRingFile" +
            " --export-secret-keys --armor")
    return normalizeGpgKey(result)
}

private fun normalizeGpgKey(key: String): String {
    // 去除--开头的行
    // 去除=开头的行
    // 去除换行符
    return key.lines().filter { !it.startsWith("--")
            && !it.startsWith("=") }.joinToString("")
}
