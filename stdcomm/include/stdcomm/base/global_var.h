//
// global_var.h
// base
//
// Created by ccgo on 2024-06-02.
// Copyright 2024 ccgo Project Authors. All rights reserved.

#ifndef STDCOMM_BASE_GLOBAL_VAR_H_
#define STDCOMM_BASE_GLOBAL_VAR_H_

#include <map>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#ifdef __ANDROID__
#  include <jni.h>
#endif

namespace stdcomm {

#define STDCOMM_GV (stdcomm::GlobalVar::GetInstance())
#define STDCOMM_DEBUG (stdcomm::GlobalVar::GetInstance().debug_)

class GlobalVar {
 private:
  GlobalVar() = default;
  ~GlobalVar() = default;
  GlobalVar(const GlobalVar &) = delete;
  GlobalVar &operator=(const GlobalVar &) = delete;

 public:
  static GlobalVar &GetInstance();

  void Clear();

  bool debug_ = false;
};

}  // namespace stdcomm

#endif  // STDCOMM_BASE_GLOBAL_VAR_H_
