# stdcomm

> Code for stdcomm common parts of Android and iOS.

- [stdcomm \- Git Intranet Version]( https///github.com/zhlinh/fext-stdcomm )

- stdcomm README

  - [English]( https///github.com/zhlinh/fext-stdcomm/blob/master/README.md )
  - [简体中文]( https///github.com/zhlinh/fext-stdcomm/blob/master/README.zh-cn.md )

- stdcomm Documentation

  - [English]( https://github.com/zhlinh/fext-stdcomm/wiki/ )
  - [简体中文]( https://github.com/zhlinh/fext-stdcomm/wiki/zh-cn/index.html )

## 1. Releases

See [releases](https///github.com/zhlinh/fext-stdcomm/-/releases) for published versions and [changelog](https///github.com/zhlinh/fext-stdcomm/blob/master/CHANGELOG.md) for version changes.

- The SDK naming convention for Android is: STDCOMM_ANDROID_SDK-`version`-`release`.aar
- The framework naming convention for iOS is: STDCOMM_IOS_FRAMEWORK-`version`-`release`.zip
- A tag named "v`version`" will be created during release, for example, v3.3.5.
- If it is a non-release development version, the `release` field will be replaced with `beta`. `submission number from the last tag` such as beta.23
- If it is a non-release version that has local uncommitted changes, the `release` field will be replaced with `beta`.`submission number from the last tag`-`dirty`. for example: beta.23-dirty

## 2. Samples

This directory contains demos for various platforms.

## 3. Getting Started

### 3.1 Android

Enter the stdcomm directory, use Android Studio's Gradle to open the project, and then execute:

```shell
./gradlew archiveProject

# If only the C++ part of Android is compiled to generate .so, you can execute
python3 ./build_android.py 1 armeabi-v7a
```

After successful compilation, aar and zip files will be generated in the `bin` directory. Aar is the necessary SDK and the zip file also saves unstripped so files.

### 3.2 iOS

Enter the stdcomm directory, and execute the following:

```shell
python3 ./build_ios.py 1

# If you need to generate iOS XCode project files (output directory is cmake_build/iOS), then execute:
python3 ./build_ios.py 2
```

After successful compilation, stdcomm.framework will be generated in `cmake_build/iOS/Darwin.out`, which is the required framework.

The external header files include in api/ directory. Version information is saved in base/verinfo.h.

### 3.3 Windows

Enter the stdcomm directory, and execute the following:

```shell
python3 ./build_windows.py 1

# If you need to generate Windows Visual Studio project files (output directory is cmake_build/Windows), then execute:
python3 ./build_windows.py 2
```

After successful compilation, stdcomm.lib will be generated in `cmake_build/Windows/Windows.out`, which is the required framework.

The external header files include api/ directory. Version information is saved in base/verinfo.h.

### 3.4 macOS

Enter the stdcomm directory, and execute the following:

```shell
python3 ./build_macos.py 1

# If you need to generate XCode project files (output directory is cmake_build/macOS), then execute:
python3 ./build_macos.py 2
```

After successful compilation, stdcomm.lib will be generated in `cmake_build/macOS/Darwin.out`, which is the required framework.

The external header files include api/ directory. Version information is saved in base/verinfo.h.

### 3.5 Linux

Enter the stdcomm directory, and execute the following:

```shell
python3 ./build_linux.py 1

# If you need to generate CodeLite project files (output directory is cmake_build/Linux), then execute:
python3 ./build_linux.py 2
```

After successful compilation, stdcomm.lib will be generated in `cmake_build/Linux/Linux.out`, which is the required framework.

The external header files include api/ directory. Version information is saved in base/verinfo.h.

## 4. Get Testes and Benches

### 4.1 GoogleTest

GoogleTest is used for unit testing. Enter the stdcomm directory and execute:

```shell
# Compile and run googletest
python3 ./build_tests.py 3 [filter] [--debuglog]
# The filter is optional and specifies the unit tests to be run. When not filled in, all unit tests are executed by default.
# For example, utils_test means only the unit tests within the utils_test test suite are executed.
# The --debuglog is optional to open debug log

# Compile only googletest
python3 ./build_tests.py 1
# Run only googletest
python3 ./build_tests.py 4


# If you want to generate relevant project files, it is XCode for MacOS, VS for Windows, and CodeLite for Linux.
python3 ./build_tests.py 2
```

After successful compilation, stdcomm_googletest will be generated in `cmake_build/googletest`, which is an executable file.

### 4.2 Benchmark

Benchmark is used for code performance analysis. Enter the stdcomm directory and execute:

```shell
# Compile and run benchmark
python3 ./build_benches.py 2
# Only compile benchmark
python3 ./build_benches.py 1
```

After successful compilation, an executable file ending with `_benchmark` will be generated in `cmake_build/benchmark`.

## 5. Contributing

### 5.1 Init Git Hooks

The project uses [cpplint](https://github.com/google/styleguide), [cppcheck](http://cppcheck.sourceforge.net/), and [lizard](https://github.com/terryyin/lizard) to perform pre-commit checks.

The stdcomm/lint directory has provided related dependencies for Windows. If you are using MacOS or Linux, please install cppcheck using brew or apt-get first.

After cloning the project, enter the stdcomm directory and execute:

```shell
# Pull the remote lint directory
git submodule update --init --recursive

# Install lint, this command only needs to be executed once
lint/install.sh cpp
```

After initialization, the following operations will be performed before each commit:

1. cpplint, cppcheck, and lizard will be executed automatically. If they don’t pass the checks, the commit will fail. This ensures that the format of committed code is uniform, Avoid common issues with static scanning, and limit cyclomatic complexity to below 20.
2. The commit message will be checked to ensure it conforms to the Google Angular Style format.

### 5.2 Style Format

The project's cpp code uses **Google**'s code style and the following tools for formatting: [clang-format](https://clang.llvm.org/docs/ClangFormat.html), [astyle](http://astyle.sourceforge.net/), and cpplint.

Enter the stdcomm directory and execute the following:

```shell
# The clangformat configuration file uses .clang-format from stdcomm/lint
# The format result is saved in stdcomm/clangformat_lint_detail.txt
lint/clangformat_project_scan.sh

# If the lint check fails (usually passes after the execution of clangformat), you can continue the repair command, which will first scan the lint, then error_fix, and finally scan the lint again to get the lint results before and after the fix.
# The error_fix result is saved in stdcomm/cpplint_error_fix_lint_detail.txt
# The lint results are saved in stdcomm/cpplint_lint_detail.txt
lint/cpplint_project_error_fix.sh

# If you only want to scan the lint and want to manually modify the result, you can execute the following command, and the result is saved in stdcomm/cpplint_lint_detail.txt
lint/cpplint_project_scan.sh
```

### 5.3 Code Check

The project’s cpp code performs static scanning using cppcheck.

Enter the stdcomm directory and execute:

```shell
# The cppcheck results are saved in stdcomm/cppcheck_lint_detail.xml
lint/cppcheck_project_scan.sh
```

### 5.4 Cyclomatic Complexity Check

The project's cyclomatic complexity check uses Lizard, ensuring the cyclomatic complexity is less than 20.

To perform this check, go to the stdcomm directory and execute:

```shell
# The Lizard cyclomatic complexity check results are saved in stdcomm/cyclomatic_complexity_lint_detail.txt
lint/cyclomatic_complexity_project_scan.sh
```

### 5.5 Commit Message Format

The project's commit message format follows the Google [Angular Style](https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit), which makes the commit history more readable and allows for the generation of changelog using the `commitizen` command-line tool.

Each commit message consists of a header, body, and footer.

```html
<header>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

The header is required and must conform to the format of a **commit message title**.

The body is optional, but if present, the body should be at least 20 characters long.

The footer is also optional and is usually used to close an issue or pull request (PR).

No line should have more than 100 characters.

**Commit Message Title**

```html
<type>(<scope>): <short summary>
│       │             │
│       │             └─⫸ Summary message, do not capitalize, and no period at the end. Note the space between the colon and the message.
│       │
│       └─⫸ Scope of the commit: stdcomm|event|http|vpn|net|base|
│                                 third_party|utils|changelog|build|readme
│
└─⫸ Type of commit: feat|fix|docs|style|refactor|test|chore|ci
```

**Type of Commit**

- feat: A new feature
- fix: A bug fix
- refactor: Code refactoring
- docs: Documentation modification
- style: Code format modification
- test: Modification of unit tests or benchmarks
- chore: Other modifications, such as build processes and dependency management
- ci: Automated commit for continuous integration

**Revert Commits**

If a commit reverts a previous commit, it should start with `revert:` followed by the commit message title of the commit being reverted.

The body of the commit message should include:

- The SHA information of the reverted commit, in the format of `This reverts commit <SHA>`
- The detailed reason for the revert.
