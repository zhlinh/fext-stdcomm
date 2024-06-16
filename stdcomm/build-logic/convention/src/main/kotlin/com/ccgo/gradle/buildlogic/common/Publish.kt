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

import org.gradle.api.Project
import org.gradle.api.publish.PublishingExtension
import org.gradle.api.publish.maven.MavenPublication
import org.gradle.kotlin.dsl.assign
import org.gradle.kotlin.dsl.configure
import org.gradle.kotlin.dsl.register
import org.gradle.plugins.signing.SigningExtension
import org.gradle.util.GradleVersion


internal fun Project.configurePublish() {
    project.afterEvaluate {
        configureMaven()
        if (GradleVersion.current() >= GradleVersion.version("4.8") && cfgs.commIsSignEnabled) {
            configureSign()
        }
    }
}

private fun Project.configureSign() {
    with(project.extensions) {
        with(pluginManager) {
            apply("signing")
        }
    }
    extensions.configure<SigningExtension> {
        sign {
            val publishing = project.extensions.getByName("publishing") as PublishingExtension
            var signingKey = getLocalProperties("signing.key", "")
            val signingPassword = getLocalProperties("signing.password", "")
            if (signingKey.isEmpty()) {
                // if empty
                var signingKeyId = getLocalProperties("signing.keyId", "")
                // 1. get key from keyId
                signingKey = getGpgKeyFromKeyId(signingKeyId, signingPassword)
                println("signing.keyId:$signingKeyId to signing.key:$signingKey")
                if (signingKey.isEmpty()) {
                    val secretKeyRingFile = getLocalProperties("signing.secretKeyRingFile", "")
                    if (secretKeyRingFile.isEmpty()) {
                        return@sign
                    }
                    // 2. get key from keyRingFile
                    signingKey = getGpgKeyFromKeyRingFile(secretKeyRingFile, signingPassword)
                    println("signing.secretKeyRingFile:$secretKeyRingFile to signing.key:$signingKey")
                }
                if (signingKey.isEmpty()) {
                    return@sign
                }
            }
            useInMemoryPgpKeys(signingKey, signingPassword)
            sign(publishing.publications.getByName("main") as MavenPublication)
        }
    }
}

/**
 * Configures the publishing for the project.
 *
 * config the url, username, password in local.properties, the format like
 * comm.maven.count=2
 * comm.maven.url0=https\://xxx.com/xx
 * comm.maven.username0=xxx
 * comm.maven.password0=xxx
 * comm.maven.url1=/Users/path/prebuilds/repository
 */
private fun Project.configureMaven() {
    with(project.extensions) {
        with(pluginManager) {
            apply("maven-publish")
        }
    }
    configureCustomMaven()
}

private fun Project.configureCustomMaven() {
    // execute "./gradlew publishMainPublicationToMavenRepository"
    extensions.configure<PublishingExtension> {
        repositories {
            val mavenCount = getLocalProperties("comm.maven.count", "0").toInt()
            val taskName = project.gradle.startParameter.taskNames.firstOrNull()
            var validMavenCount = 0
            if (mavenCount > 0) {
                for (i in 0 until mavenCount) {
                    val url = getLocalProperties("comm.maven.url${i}", "")
                    val username = getLocalProperties("comm.maven.username${i}", "")
                    val password = getLocalProperties("comm.maven.password${i}", "")
                    if (url.isEmpty()) {
                        continue
                    }
                    validMavenCount++
                    maven {
                        if (mavenCount > 1 && i != 0) {
                            this.name = "maven${i}"
                        }
                        this.url = uri(url)
                        if (username.isNotEmpty() && password.isNotEmpty()) {
                            credentials {
                                this.username = username
                                this.password = password
                            }
                        }
                    }
                }
            } else {
                // 获取当前运行的任务名
                if (taskName != null && taskName.contains("publish")) {
                    throw Exception( getErrorHint(hintCount = true) )
                } else {
                    println( getErrorHint(hintCount = false) )
                }
            }
            if (validMavenCount == 0) {
                // 获取当前运行的任务名
                if (taskName != null && taskName.contains("publish")) {
                    throw Exception( getErrorHint(hintCount = false) )
                } else {
                    println( getErrorHint(hintCount = false) )
                }
            }
        }

        val publishConfig = mutableMapOf(
            // main always use release
            "main" to "bin/${cfgs.projectNameUppercase}_ANDROID_SDK-${cfgs.versionName}-release.aar",
        )
        if (!cfgs.isRelease) {
            // if not release, add test publication
            publishConfig["test"] = "bin/${cfgs.mainProjectArchiveAarName}"
        }
        publications {
            for ((publishName, artifactName) in publishConfig) {
                register(publishName, MavenPublication::class) {
                    groupId = cfgs.commGroupId
                    artifactId = cfgs.projectNameLowercase
                    if (publishName == "main") {
                        version = cfgs.versionName
                    } else {
                        version = "${cfgs.versionName}-TEST"
                    }
                    // add artifact aar
                    artifact(artifactName)

                    // add pom
                    pom {
                        name = cfgs.projectName
                        description = "The ${cfgs.projectName} SDK"
//                        url = getGitRepoUrl()

                        licenses {
                            license {
                                name = "MIT License"
                                url = "https://opensource.org/licenses/MIT"
                            }
                        }
                        developers {
                            developer {
                                id = getGitRepoUserName()
                                name = getGitRepoUserName()
                                email = getGitRepoUserEmail()
                            }
                        }

                        withXml {
                            println("groupId: $groupId")
                            println("artifactId: $artifactId")
                            println("version: $version")
                            println("artifactName: $artifactName")
                            println("------------")
                            val commDependencies = cfgs.commDependenciesAsList
                            if (commDependencies.isEmpty()) {
                                return@withXml
                            }
                            val dependenciesNode = asNode().appendNode("dependencies")
                            for (dependency in commDependencies) {
                                val dependencyNode = dependenciesNode.appendNode("dependency")
                                val parts = dependency.split(":")
                                println("add dependency: $parts")
                                dependencyNode.appendNode("groupId", parts[0])
                                dependencyNode.appendNode("artifactId", parts[1])
                                dependencyNode.appendNode("version", parts[2])
                            }  // dependencies
                        }  // withXml
                    }  // pom
                }  // MavenPublication
            }  // for
        }  // publications
    }  // PublishingExtension
}

private fun getErrorHint(hintCount: Boolean): String {
    val hintCountStr = if (hintCount) "\ncomm.maven.count=1" else ""
    return "【Error】[Publish-Configuration] failed to get comm.maven.count, you need to add" +
            " at least one maven config in local.properties" +
            hintCountStr +
            "\ncomm.maven.url0=<MAVEN_URL>" +
            "\ncomm.maven.username0=<USERNAME>" +
            "\ncomm.maven.password0=<PASSWORD>"
}
