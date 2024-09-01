# stdcomm

> Android和iOS的基础库公共部分的代码

- [stdcomm \- 工蜂内网版]( https://github.com/zhlinh/fndyext-stdcomm )

- stdcomm README
  
  - [English]( https://github.com/zhlinh/fndyext-stdcomm/blob/master/README.md )
  - [简体中文]( https://github.com/zhlinh/fndyext-stdcomm/blob/master/README.zh-cn.md )

- stdcomm Documentation
  
  - [English]( http://fndyext-stdcomm.pages.oa.com/ )
  - [简体中文]( http://fndyext-stdcomm.pages.oa.com/zh-cn/index.html )

## 1. Releases

发布版本见[releases](https://github.com/zhlinh/fndyext-stdcomm/-/releases)，版本变更记录见[changelog](https://github.com/zhlinh/fndyext-stdcomm}/blob/master/CHANGELOG.md)

- Android的sdk命名规则为: stdcomm_ANDROID_SDK-`版本号`-`release`.aar
- iOS的framework命名规则为: stdcomm_IOS_FRAMEWORK-`版本号`-`release`.zip
- 在release的时候会打TAG，命名规则为: v`版本号`，如v3.3.5
- 如果是非release的开发版本，则`release`字段会被替换为`beta`.`从上一次TAG开始的提交次数`，如beta.23
- 如果是非release，本地有修改且未提交的版本，则`release`字段会被替换为`beta`.`从上一次TAG开始的提交次数`-`dirty`，如beta.23-dirty

## 2. Samples

该目录为各平台的demo

## 3. Getting start with stdcomm

### 3.1 Android

进入stdcomm目录，使用android studio的gradle打开该工程，然后执行

```shell
./gradlew archiveProject

# 如果只编译Android的C++部分生成so，则可执行
python3 ./build_android.py 1 armeabi-v7a
```

编译成功后会在bin目录下生成aar和zip文件，aar为所需的sdk，zip文件除了sdk还保存了未strip的so等文件

### 3.2 iOS

进入stdcomm目录，执行

```shell
python3 ./build_ios.py 1

# 如果需要生成iOS的XCode项目文件(输出目录是cmake_build/iOS)，则可执行
python3 ./build_ios.py 2
```

编译成功后会在cmake_build/iOS/Darwin.out中生成stdcomm.framework，此目录即所需的framework

对外的头文件有api/stdcommLog.h。版本信息保存在base/verinfo.h中

### 3.3 Windows

进入stdcomm目录，执行

```shell
python3 ./build_windows.py 1

# 如果需要生成Windows的Visual Studio项目文件(输出目录是cmake_build/Windows)，则可执行
python3 ./build_windows.py 2
```

编译成功后会在cmake_build/Windows/Windows.out中生成stdcomm.framework，此目录即所需的framework

对外的头文件有api/stdcommLog.h。版本信息保存在base/verinfo.h中

### 3.4 macOS

进入stdcomm目录，执行

```shell
python3 ./build_macos.py 1

# 如果需要生成macOS的XCode项目文件(输出目录是cmake_build/macOS)，则可执行
python3 ./build_macos.py 2
```

编译成功后会在cmake_build/macOS/Darwin.out中生成stdcomm.framework，此目录即所需的framework

对外的头文件在api/文件夹中。版本信息保存在base/verinfo.h中

### 3.5 Linux

进入stdcomm目录，执行

```shell
python3 ./build_linux.py 1

# 如果需要生成Linux的CodeLite项目文件(输出目录是cmake_build/Linux)，则可执行
python3 ./build_linux.py 2
```

编译成功后会在cmake_build/Linux/Linux.out中生成stdcomm.framework，此目录即所需的framework

对外的头文件在api/文件夹中。版本信息保存在base/verinfo.h中

## 4. Get Testes and Benches

### 4.1 GoogleTest

GoogleTest用于单元测试。进入stdcomm目录，执行

```shell
# 编译并运行googletest
python3 ./build_tests.py 3 [filter] [--debuglog]
# 其中filter选填，指的是仅执行部分的单元测试，不填时默认执行所有单元测试
# 例如utils_test表示只执行utils_test测试集合中的单元测试
# --debuglog选项为打开调试日志

# 仅编译googletest
python3 ./build_tests.py 1
# 仅运行googletest
python3 ./build_tests.py 4 [filter] [--debuglog]


# 如果想生成相关的项目文件，MacOS为XCode，Windows为VS，Linux为CodeLite
python3 ./build_googletest.py 1
```

编译成功后会在cmake_build/googletest目录中生成stdcomm_googletest的可执行文件


### 4.2 Benchmark

Benchmark用于代码性能分析。进入stdcomm目录，执行

```shell
# 编译并运行benchmark
python3 ./build_benches.py 2
# 仅编译benchmark
python3 ./build_benches.py 1
```

编译成功后会在cmake_build/benchmark目录中生成`_benchmark`结尾的可执行文件


## 5. Contributing

### 5.1 Init git hooks

项目使用[cpplint](https://github.com/google/styleguide)、[cppcheck](http://cppcheck.sourceforge.net/)和[lizard](https://github.com/terryyin/lizard)进行pre-commit的检查

stdcomm/lint目录已提供Windows的相关依赖，如果是MacOS或Linux，请先通过brew或apt-get安装cppcheck

clone项目后，进入stdcomm目录执行

```shell
# 拉取远程的lint目录
git submodule update --init --recursive

# 安装lint，该命令只需执行一次
lint/install.sh cpp
```

init之后，每次commit前会

1. 自动执行cpplint、cppcheck和lizard，若不通过检查则commit失败。从而保证提交成功的代码格式统一，避免静态扫描的常见问题，并限制圈复杂度在20以下
2. 检查commit的提交消息，格式为Google的Angular Style

### 5.2 Style format

项目cpp部分使用**Google**的代码风格，format使用的工具有[clang-format](https://clang.llvm.org/docs/ClangFormat.html)，[astyle](http://astyle.sourceforge.net/)和cpplint

进入stdcomm目录，执行

```shell
# clangformat的配置文件使用的是stdcomm/lint的.clang-format
# format的结果保存在stdcomm/clangformat_lint_detail.txt
lint/clangformat_project_scan.sh

# 如果还未通过lint检查（通常执行clangformat后都会通过lint），则可继续执行修复命令，该命令会先扫描lint，再error_fix，最后再次扫描lint，即得到修复前后的lint结果
# error_fix的结果保存在stdcomm/cpplint_error_fix_lint_detail.txt
# lint的结果保存在stdcomm/cpplint_lint_detail.txt
lint/cpplint_project_error_fix.sh

# 如果只是扫描lint，想手动修改的话，可以执行以下命令，结果保存在stdcomm/cpplint_lint_detail.txt
lint/cpplint_project_scan.sh
```

### 5.3 Code check

项目cpp的代码静态扫描使用cppcheck

进入stdcomm目录，执行

```shell
# cppcheck的结果保存在stdcomm/cppcheck_lint_detail.xml
lint/cppcheck_project_scan.sh
```

### 5.4 Cyclomatic Complexity Check

项目的圈复杂度检查使用lizard，保证圈复杂度在20以下。

进入stdcomm目录，执行

```shell
# lizard圈复杂度检查的结果保存在stdcomm/cyclomatic_complexity_lint_detail.txt
lint/cyclomatic_complexity_project_scan.sh
```

### 5.5 Commit Message Format

项目的提交消息格式为Google的[Augular Style]( https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit )，使用这种格式可以让提交的历史记录更具可读性，并可使用`commitizen`命令行工具来自动生成版本变更记录CHANGELOG。

每个提交消息都是由header，body和footer组成

```html
<header>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

header是必需的，并且必须符合**提交消息标题**的格式

body是可选的，但如果有body请保证body至少大于20个字符

footer是可选的，通常是关闭了某个ISSUE或者某个PR(Pull Request)

所有行数的字符不要大于100个字符

**提交消息标题**

```html
<type>(<scope>): <short summary>
│       │             │
│       │             └─⫸ 摘要消息，不要大写，最后没有句号，注意与前面的冒号之间有一个空格
│       │
│       └─⫸ 提交范围:   stdcomm|event|http|vpn|net|base|
│                      third_party|utils|changelog|build|readme
│
└─⫸ 提交类型: feat|fix|docs|style|refactor|test|chore|ci
```

**提交类型**

- feat: 新特性
- fix: 修复问题
- refactor: 代码重构
- docs: 文档修改
- style: 代码格式修改
- test: 单元测试或benchmark修改
- chore: 其他修改，比如构建流程、依赖管理
- ci: 持续构建的自动化提交

**Revert commits**

如果某提交revert了之前的提交，则应以`revert:`开头，接着是所revert的提交消息标题

提交消息body的内容应该包括：

- 所revert提交的SHA信息，格式为：`This reverts commit <SHA>`
- revert的详细原因
