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

val rootProjectName = rootDir.absolutePath.split("/").last().lowercase()
println("rootProjectName: $rootProjectName")
rootProject.name = rootProjectName

pluginManagement {
    includeBuild("build-logic")
    repositories {
        google()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

include(":android:main_android_sdk")
include(":android:empty_android_lib_to_recognise_cpp")

