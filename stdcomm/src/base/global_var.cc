//
// global_var.cpp
// base
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#include "stdcomm/base/global_var.h"

namespace stdcomm {

GlobalVar &GlobalVar::GetInstance() {
  static GlobalVar instance;
  return instance;
}

void GlobalVar::Clear() {}

}  // namespace stdcomm
