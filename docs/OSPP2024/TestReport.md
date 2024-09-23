> Corrector: [TinyCorrect](https://gitee.com/tinylab/tinycorrect) v0.2-rc2 - [tables]<br/>

# 测试报告

## 受测环境

|   | OS                          | python | 原生 package manager |
|---|-----------------------------|--------|----------------------|
| 1 | fedora 40                   | 3.9.19 | dnf 4.21.1           |
| 2 | debian 12 bookworm          | 3.11.2 | apt 2.6.1            |
| 3 | archlinux 20240804.0.251467 | 3.12.5 | pacman 6.1.0         |

## 测试结果

通过 [asciinema](https://asciinema.org/) 自动执行命令并记录输出。

### Fedora

#### 软件安装与 pytest 测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

# in tinyget project root
asciinema rec --overwrite -c "make" -t "Tinyget Build ${name}" tinyget-build-${name}.cast
```

结果演示：

[![asciicast](https://asciinema.org/a/677182.svg)](https://asciinema.org/a/677182)

#### 基本操作测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

asciinema rec --overwrite -c "$(cat testCmds.sh)" -t "Tinyget Test ${name}" tinyget-test-${name}.cast
```

```bash
# 测试命令（testCmds.sh）
echo -e "\033[32m\ntinyget-user >> cat /etc/os-release\n\033[0m"
sleep 1
cat /etc/os-release
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --help\n\033[0m"
sleep 1
tinyget --help
testHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget config --help\n\033[0m"
sleep 1
tinyget config --help
testConfigHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget history\n\033[0m"
sleep 1
tinyget history
testHistoryCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget search gcc\n\033[0m"
sleep 1
tinyget search gcc
testSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --no-live-output search gcc\n\033[0m"
sleep 1
tinyget --no-live-output search gcc
testNoLiveOutputSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_list\n\033[0m"
sleep 1
tinyget repo_list
testRepoListCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_configure debian\n\033[0m"
sleep 1
tinyget repo_configure debian
testRepoConfigCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> pkexec tinyget install tmux-top\n\033[0m"
sleep 1
pkexec tinyget install tmux-top
testInstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> pkexec tinyget uninstall tmux-top\n\033[0m"
sleep 1
pkexec tinyget uninstall tmux-top
testUninstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> pkexec tinyget install not-found-softs\n\033[0m"
sleep 1
pkexec tinyget install not-found-softs
testInstallNotFoundCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> pkexec tinyget update\n\033[0m"
sleep 1
pkexec tinyget update
testUpdateCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> pkexec tinyget upgrade\n\033[0m"
sleep 1
pkexec tinyget upgrade
testUpgradeCli=$?
sleep 1

if [[ $testHelpCli == 0 ]]; then
    echo -e "\033[32m Test Help Cli success \033[0m"
else
    echo -e "\e[31m Test Help Cli Error \e[0m"
fi

if [[ $testConfigHelpCli == 0 ]]; then
    echo -e "\033[32m Test Config Help Cli success \033[0m"
else
    echo -e "\e[31m Test Config Help Cli Error \e[0m"
fi

if [[ $testHistoryCli == 0 ]]; then
    echo -e "\033[32m Test History Cli success \033[0m"
else
    echo -e "\e[31m Test History Cli Error \e[0m"
fi

if [[ $testSearchCli == 0 ]]; then
    echo -e "\033[32m Test Search Cli success \033[0m"
else
    echo -e "\e[31m Test Search Cli Error \e[0m"
fi

if [[ $testNoLiveOutputSearchCli == 0 ]]; then
    echo -e "\033[32m Test No Live Output Search Cli success \033[0m"
else
    echo -e "\e[31m Test No Live Output Search Cli Error \e[0m"
fi

if [[ $testRepoListCli == 0 ]]; then
    echo -e "\033[32m Test Repo List Cli success \033[0m"
else
    echo -e "\e[31m Test Repo List Cli Error \e[0m"
fi

if [[ $testRepoConfigCli == 0 ]]; then
    echo -e "\033[32m Test Repo Config Cli success \033[0m"
else
    echo -e "\e[31m Test Repo Config Cli Error \e[0m"
fi

if [[ $testInstallCli == 0 ]]; then
    echo -e "\033[32m Test Install Cli success \033[0m"
else
    echo -e "\e[31m Test Install Cli Error \e[0m"
fi

if [[ $testUninstallCli == 0 ]]; then
    echo -e "\033[32m Test Uninstall Cli success \033[0m"
else
    echo -e "\e[31m Test Uninstall Cli Error \e[0m"
fi

if [[ $testInstallNotFoundCli != 0 ]]; then
    echo -e "\033[32m Test Install Not Found Cli success \033[0m"
else
    echo -e "\e[31m Test Install Not Found Cli Error \e[0m"
fi

if [[ $testUpdateCli == 0 ]]; then
    echo -e "\033[32m Test Update Cli success \033[0m"
else
    echo -e "\e[31m Test Update Cli Error \e[0m"
fi

if [[ $testUpgradeCli == 0 ]]; then
    echo -e "\033[32m Test Upgrade Cli success \033[0m"
else
    echo -e "\e[31m Test Upgrade Cli Error \e[0m"
fi
```

结果演示：

[![asciicast](https://asciinema.org/a/677177.svg)](https://asciinema.org/a/677177)

### ArchLinux

#### 软件安装与 pytest 测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

# in tinyget project root
asciinema rec --overwrite -c "make" -t "Tinyget Build ${name}" tinyget-build-${name}.cast
```

结果演示：

[![asciicast](https://asciinema.org/a/677186.svg)](https://asciinema.org/a/677186)

#### 基本操作测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

asciinema rec --overwrite -c "$(cat testCmds.sh)" -t "Tinyget Test ${name}" tinyget-test-${name}.cast
```

```bash
# 测试命令（testCmds.sh）
echo -e "\033[32m\ntinyget-user >> cat /etc/os-release\n\033[0m"
sleep 1
cat /etc/os-release
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --help\n\033[0m"
sleep 1
tinyget --help
testHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget config --help\n\033[0m"
sleep 1
tinyget config --help
testConfigHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget history\n\033[0m"
sleep 1
tinyget history
testHistoryCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget search gcc\n\033[0m"
sleep 1
tinyget search gcc
testSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --no-live-output search gcc\n\033[0m"
sleep 1
tinyget --no-live-output search gcc
testNoLiveOutputSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_list\n\033[0m"
sleep 1
tinyget repo_list
testRepoListCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_configure archlinux\n\033[0m"
sleep 1
tinyget repo_configure archlinux
testRepoConfigCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget install tmux\n\033[0m"
sleep 1
tinyget install tmux
testInstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget uninstall tmux\n\033[0m"
sleep 1
tinyget uninstall tmux
testUninstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget install not-found-softs\n\033[0m"
sleep 1
tinyget install not-found-softs
testInstallNotFoundCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget update\n\033[0m"
sleep 1
tinyget update
testUpdateCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget upgrade\n\033[0m"
sleep 1
tinyget upgrade
testUpgradeCli=$?
sleep 1

if [[ $testHelpCli == 0 ]]; then
    echo -e "\033[32m Test Help Cli success \033[0m"
else
    echo -e "\e[31m Test Help Cli Error \e[0m"
fi

if [[ $testConfigHelpCli == 0 ]]; then
    echo -e "\033[32m Test Config Help Cli success \033[0m"
else
    echo -e "\e[31m Test Config Help Cli Error \e[0m"
fi

if [[ $testHistoryCli == 0 ]]; then
    echo -e "\033[32m Test History Cli success \033[0m"
else
    echo -e "\e[31m Test History Cli Error \e[0m"
fi

if [[ $testSearchCli == 0 ]]; then
    echo -e "\033[32m Test Search Cli success \033[0m"
else
    echo -e "\e[31m Test Search Cli Error \e[0m"
fi

if [[ $testNoLiveOutputSearchCli == 0 ]]; then
    echo -e "\033[32m Test No Live Output Search Cli success \033[0m"
else
    echo -e "\e[31m Test No Live Output Search Cli Error \e[0m"
fi

if [[ $testRepoListCli == 0 ]]; then
    echo -e "\033[32m Test Repo List Cli success \033[0m"
else
    echo -e "\e[31m Test Repo List Cli Error \e[0m"
fi

if [[ $testRepoConfigCli == 0 ]]; then
    echo -e "\033[32m Test Repo Config Cli success \033[0m"
else
    echo -e "\e[31m Test Repo Config Cli Error \e[0m"
fi

if [[ $testInstallCli == 0 ]]; then
    echo -e "\033[32m Test Install Cli success \033[0m"
else
    echo -e "\e[31m Test Install Cli Error \e[0m"
fi

if [[ $testUninstallCli == 0 ]]; then
    echo -e "\033[32m Test Uninstall Cli success \033[0m"
else
    echo -e "\e[31m Test Uninstall Cli Error \e[0m"
fi

if [[ $testInstallNotFoundCli != 0 ]]; then
    echo -e "\033[32m Test Install Not Found Cli success \033[0m"
else
    echo -e "\e[31m Test Install Not Found Cli Error \e[0m"
fi

if [[ $testUpdateCli == 0 ]]; then
    echo -e "\033[32m Test Update Cli success \033[0m"
else
    echo -e "\e[31m Test Update Cli Error \e[0m"
fi

if [[ $testUpgradeCli == 0 ]]; then
    echo -e "\033[32m Test Upgrade Cli success \033[0m"
else
    echo -e "\e[31m Test Upgrade Cli Error \e[0m"
fi
```

结果演示：

[![asciicast](https://asciinema.org/a/677184.svg)](https://asciinema.org/a/677184)

### Debian

#### 软件安装与 pytest 测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

# in tinyget project root
asciinema rec --overwrite -c "make" -t "Tinyget Build ${name}" tinyget-build-${name}.cast
```

结果演示：

[![asciicast](https://asciinema.org/a/677181.svg)](https://asciinema.org/a/677181)

#### 基本操作测试

```bash
# asciinema 脚本
#!/bin/bash

if [[ -z $1 ]]; then
    echo "please provide a test name"
    exit 1
fi

name=$1

asciinema rec --overwrite -c "bash -c '$(cat testCmds.sh)'" -t "Tinyget Test ${name}" tinyget-test-${name}.cast
```

```bash
# 测试命令（testCmds.sh）
echo -e "\033[32m\ntinyget-user >> cat /etc/os-release\n\033[0m"
sleep 1
cat /etc/os-release
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --help\n\033[0m"
sleep 1
tinyget --help
testHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget config --help\n\033[0m"
sleep 1
tinyget config --help
testConfigHelpCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget history\n\033[0m"
sleep 1
tinyget history
testHistoryCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget search gcc\n\033[0m"
sleep 1
tinyget search gcc
testSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget --no-live-output search gcc\n\033[0m"
sleep 1
tinyget --no-live-output search gcc
testNoLiveOutputSearchCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_list\n\033[0m"
sleep 1
tinyget repo_list
testRepoListCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget repo_configure debian\n\033[0m"
sleep 1
tinyget repo_configure debian
testRepoConfigCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget install tmux\n\033[0m"
sleep 1
tinyget install tmux
testInstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget uninstall tmux\n\033[0m"
sleep 1
tinyget uninstall tmux
testUninstallCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget install not-found-softs\n\033[0m"
sleep 1
tinyget install not-found-softs
testInstallNotFoundCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget update\n\033[0m"
sleep 1
tinyget update
testUpdateCli=$?
sleep 1

echo -e "\033[32m\ntinyget-user >> tinyget upgrade\n\033[0m"
sleep 1
tinyget upgrade
testUpgradeCli=$?
sleep 1

if [[ $testHelpCli == 0 ]]; then
    echo -e "\033[32m Test Help Cli success \033[0m"
else
    echo -e "\e[31m Test Help Cli Error \e[0m"
fi

if [[ $testConfigHelpCli == 0 ]]; then
    echo -e "\033[32m Test Config Help Cli success \033[0m"
else
    echo -e "\e[31m Test Config Help Cli Error \e[0m"
fi

if [[ $testHistoryCli == 0 ]]; then
    echo -e "\033[32m Test History Cli success \033[0m"
else
    echo -e "\e[31m Test History Cli Error \e[0m"
fi

if [[ $testSearchCli == 0 ]]; then
    echo -e "\033[32m Test Search Cli success \033[0m"
else
    echo -e "\e[31m Test Search Cli Error \e[0m"
fi

if [[ $testNoLiveOutputSearchCli == 0 ]]; then
    echo -e "\033[32m Test No Live Output Search Cli success \033[0m"
else
    echo -e "\e[31m Test No Live Output Search Cli Error \e[0m"
fi

if [[ $testRepoListCli == 0 ]]; then
    echo -e "\033[32m Test Repo List Cli success \033[0m"
else
    echo -e "\e[31m Test Repo List Cli Error \e[0m"
fi

if [[ $testRepoConfigCli == 0 ]]; then
    echo -e "\033[32m Test Repo Config Cli success \033[0m"
else
    echo -e "\e[31m Test Repo Config Cli Error \e[0m"
fi

if [[ $testInstallCli == 0 ]]; then
    echo -e "\033[32m Test Install Cli success \033[0m"
else
    echo -e "\e[31m Test Install Cli Error \e[0m"
fi

if [[ $testUninstallCli == 0 ]]; then
    echo -e "\033[32m Test Uninstall Cli success \033[0m"
else
    echo -e "\e[31m Test Uninstall Cli Error \e[0m"
fi

if [[ $testInstallNotFoundCli != 0 ]]; then
    echo -e "\033[32m Test Install Not Found Cli success \033[0m"
else
    echo -e "\e[31m Test Install Not Found Cli Error \e[0m"
fi

if [[ $testUpdateCli == 0 ]]; then
    echo -e "\033[32m Test Update Cli success \033[0m"
else
    echo -e "\e[31m Test Update Cli Error \e[0m"
fi

if [[ $testUpgradeCli == 0 ]]; then
    echo -e "\033[32m Test Upgrade Cli success \033[0m"
else
    echo -e "\e[31m Test Upgrade Cli Error \e[0m"
fi
```

结果演示：

[![asciicast](https://asciinema.org/a/677183.svg)](https://asciinema.org/a/677183)

### 结论

所有测试均通过，能在受测系统上完成打包安装，同时基本操作输出也符合预期。
