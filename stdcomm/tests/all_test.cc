//
// all_test.cc
// tests
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#include "gtest/gtest.h"

static void CheckDebugLog(int argc, char **argv) {
  // if has --debug in argv then open debug log
  bool is_debug = false;
  for (int i = 0; i < argc; ++i) {
    if (strcmp(argv[i], "--debuglog") == 0) {
      is_debug = true;
      break;
    }
  }
  if (is_debug) {
    // FIXME: add some work here
  }
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);

  CheckDebugLog(argc, argv);

  // Filter part of TestCase to run
  // suggest to use command line parameter directly `--gtest_filter=ApiTest*`
  // or set environment variable `export GTEST_FILTER="ApiTest*"`
  // ::testing::GTEST_FLAG(filter) = "ApiTest*";

  // Runs all tests using Google Test.
  return RUN_ALL_TESTS();
}
