//
// api_test.cc
// api
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#include "stdcomm/api/native/stdcomm.h"

#include <string>

#include "gtest/gtest.h"

namespace stdcomm {

TEST(ApiTest, testDebuglog) {
  stdcomm_SetDebugLog(true);
  // TODO: add test code here
  ASSERT_TRUE(1 == 1);
}

}  // namespace stdcomm
