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

import com.ccgo.gradle.buildlogic.common.utils.getCurrentTag
import com.ccgo.gradle.buildlogic.common.utils.getGitBranchName
import com.ccgo.gradle.buildlogic.common.utils.getGitHeadTimeInfo
import com.ccgo.gradle.buildlogic.common.utils.getGitRevision
import com.ccgo.gradle.buildlogic.common.utils.getGitVersionCode
import com.ccgo.gradle.buildlogic.common.utils.getPublishSuffix
import org.gradle.api.JavaVersion
import org.gradle.api.Project
import org.gradle.configurationcache.extensions.capitalized
import org.gradle.kotlin.dsl.extra

/**
 * Project config
 */
class ProjectConfig(val project: Project) {
    companion object {
        private var projectConfig: ProjectConfig? = null
        fun getDefault(project: Project): ProjectConfig {
            return projectConfig ?: ProjectConfig(project).also {
                projectConfig = it
                it.print()
            }
        }
    }

    val mainCommProject
        get(): Project = project.rootProject.subprojects.find { it.name.startsWith("main") && !it.name.startsWith("empty") }!!
    val javaCompatibilityVersion = JavaVersion.VERSION_11
    val gradlePluginJavaCompatibilityVersion = JavaVersion.VERSION_17
    val versionName: String = project.libs.findVersion("commMainProject").get().toString()
    val isRelease: Boolean = project.libs.findVersion("commIsRelease").get().toString().toBoolean()
    val commGroupId: String = project.libs.findVersion("commGroupId").get().toString()
    val commAndroidStl: String = project.libs.findVersion("commAndroidStl").get().toString()
    private val commAndroidStlIsStatic: Boolean = commAndroidStl.endsWith("_static")
    val androidStlSuffix = if (commAndroidStlIsStatic) "-stdembed" else ""
    val commDependencies: String =
        project.libs.findVersion("commDependencies").get().toString().replace("\\s".toRegex(), "")
    // remove blanks
    val commDependenciesAsList: List<String> = commDependencies.split(",")
            .filter {
                it.isNotBlank() && it != "EMPTY" && it.contains(":")
            }
    val commIsSignEnabled: Boolean = project.libs.findVersion("commIsSignEnabled").get().toString().toBoolean()
    val versionCode: String by lazy { getGitVersionCode() }
    val revision: String by lazy { getGitRevision() }
    val branchName: String by lazy { getGitBranchName() }
    val timeInfo: String by lazy { getGitHeadTimeInfo() }
    val publishSuffix: String by lazy { getPublishSuffix(isRelease) }
    val currentTag: String = getCurrentTag(isRelease, versionName, publishSuffix)
    val projectName: String = project.rootProject.projectDir.name.split("/").last().uppercase()
    val projectNameUppercase: String = projectName.uppercase()
    val projectNameLowercase: String = projectName.lowercase()
    val mainProjectArchiveAarName = getMainArchiveAarName(publishSuffix)
    val mainProjectArchiveZipName = "(ARCHIVE)_${mainProjectArchiveAarName.removeSuffix(".aar")}.zip"

    // flavor prod
    val mainProjectAssembleProdTaskName = "assemble${ProjectFlavor.prod.name.capitalized()}Release"
    val mainProjectMergeProdJniTaskName = "merge${ProjectFlavor.prod.name.capitalized()}ReleaseJniLibFolders"

    // flavor debug
    val mainProjectAssembleDemoTaskName = "assemble${ProjectFlavor.demo.name.capitalized()}Release"
    val mainProjectMergeDemoJniTaskName = "merge${ProjectFlavor.demo.name.capitalized()}ReleaseJniLibFolders"

    // flavor debug
    // all flavor
    val mainProjectAssembleAllTaskName = "assembleRelease"
    val mainProjectMergeJniTaskName = "mergeReleaseJniLibFolders"

    val compileSdkVersion: Int = project.libs.findVersion("compileSdkVersion").get().toString().toInt()
    val buildToolsVersion: String = project.libs.findVersion("buildToolsVersion").get().toString()
    val minSdkVersion: Int = project.libs.findVersion("minSdkVersion").get().toString().toInt()
    val appMinSdkVersion: Int = project.libs.findVersion("appMinSdkVersion").get().toString().toInt()
    val targetSdkVersion: Int = project.libs.findVersion("targetSdkVersion").get().toString().toInt()

    // remove blanks
    val cmakeAbiFilters: String =
        project.libs.findVersion("cmakeAbiFilters").get().toString().replace("\\s".toRegex(), "")
    val cmakeAbiFiltersAsList: List<String> = cmakeAbiFilters.split(",")
            .filter { it.isNotBlank() && it != "EMPTY" }
    val cmakeVersion: String = project.libs.findVersion("cmakeVersion").get().toString()

    //  ndkVersion is r25c
    val ndkVersion: String = project.libs.findVersion("ndkVersion").get().toString()
    val ndkPath: String = System.getenv("NDK_ROOT") ?: ""
    val taskPrintPrefixFilters = listOf("assemble", "bundle", "publish", "merge")

    fun getMainArchiveAarName(inputSuffix: String): String {
        return "${projectNameUppercase}_ANDROID${androidStlSuffix.uppercase()}_SDK-${versionName}-${inputSuffix}.aar"
    }

    fun print() {
        println("===============CCGO Build System=================")
        println("TASKS (which can be executed by './gradlew :taskName')")
        println(":archiveProject                           - Archive the project")
        println(":publishMainPublicationToMavenRepository  - Publish Release only to maven, set config in local.properties first")
        println(":publishTestPublicationToMavenRepository  - Publish Current(Release or Beta) to maven, set config in local.properties first")
        println(":pushSo                                   - Push so files to device")
        println(":rmSo                                     - Remove so files from device")
        println(":tagGit                                   - Make a tag to git")
        println(":tasks                                    - Show all the tasks names")
        println(":printModulePaths                         - Print all the module paths")
        println("===========================================")
        println("$projectName versionName:${versionName}")
        println("$projectName versionCode:${versionCode}")
        println("$projectName revision:${revision}")
        println("$projectName branchName:${branchName}")
        println("$projectName timeInfo:${timeInfo}")
        println("$projectName isRelease:${isRelease}")
        println("$projectName publishSuffix:${publishSuffix}")
        println("$projectName currentTag:${currentTag}")
        println("$projectName androidStl:${commAndroidStl}")
        println("$projectName dependencies:${commDependencies}")
        println("===========================================")
    }
}

