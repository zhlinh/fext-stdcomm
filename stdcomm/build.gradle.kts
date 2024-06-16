//
//  Copyright 2024 zhlinh and ccgo Project Authors. All rights reserved.
//  Use of this source code is governed by a MIT-style
//  license that can be found at
//
//  https://opensource.org/license/MIT
//
//  The above copyright notice and this permission
//  notice shall be included in all copies or
//  substantial portions of the Software.

// Lists all plugins used throughout the project
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.android.test) apply false
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.maven.publish) apply false
    // ccgo plugins
    alias(libs.plugins.ccgo.android.library.native.python) apply false
    alias(libs.plugins.ccgo.android.library.native.empty) apply false
    // root plugin "apply true" here
    alias(libs.plugins.ccgo.android.root) apply true
}

// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
    repositories {
        google()
        mavenCentral()
        // Android Build Server For Test or Cache
        maven { url = uri("../ccgo-prebuilts/m2repository") }
    }
}

