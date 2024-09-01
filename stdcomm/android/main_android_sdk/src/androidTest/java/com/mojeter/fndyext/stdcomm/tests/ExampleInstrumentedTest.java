//
// ExampleInstrumentedTest.java
// tests
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

package com.mojeter.fndyext.stdcomm.tests;

import static org.junit.Assert.assertEquals;

import android.content.Context;
import android.util.Log;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import com.mojeter.fndyext.stdcomm.wrapper.StdComm;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

/**
 * Instrumented test, which will execute on an Android device.
 *
 * @see <a href="https://developer.android.com/studio/test?hl=zh-cn">Testing documentation</a>
 */
@RunWith(AndroidJUnit4.class)
public class ExampleInstrumentedTest {
    private static final String TAG = "test-" + System.currentTimeMillis();
    private Context mAppContext = null;

    @Before
    public void setUp() {
        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                // initial jobs
                mAppContext = ApplicationProvider.getApplicationContext();
                Log.d(TAG, "init start");
                Log.d(TAG, "init finish");
            }
        });
    }

    @After
    public void tearDown() {
        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
            }
        });
    }

    @Test
    public void getPackageName() {
        Log.d(TAG, "testPackageName start");
        assertEquals("com.mojeter.fndyext.stdcomm.test", mAppContext.getPackageName());
    }
    @Test
    public void setDebug() {
        InstrumentationRegistry.getInstrumentation().runOnMainSync(new Runnable() {
            @Override
            public void run() {
                StdComm.setDebugLog(true);
            }
        });
    }
}
