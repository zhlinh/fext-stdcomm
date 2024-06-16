package com.mojeter.app.sample.common

import androidx.compose.ui.window.Application
import com.mojeter.app.sample.common.App
import platform.UIKit.UIViewController

fun MainViewController(): UIViewController =
    Application("Example Application") {
        App()
    }