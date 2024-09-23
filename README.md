> Corrector: [TinyCorrect](https://gitee.com/tinylab/tinycorrect) v0.2-rc2 - [urls]<br/>
<p align="center">
	<img src="/images/logo.png" style="width: 200px"></img>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Fedora - dnf - ?logo=fedora">
    <img src="https://img.shields.io/badge/CentOS - dnf - ?logo=CentOS">
    <img src="https://img.shields.io/badge/ArchLinux - pacman - ?logo=ArchLinux">
    <img src="https://img.shields.io/badge/Debian - apt - ?logo=Debian">
    <img src="https://img.shields.io/badge/Ubuntu - apt - ?logo=Ubuntu">
    <img src="https://img.shields.io/badge/license-GPL%20v2-yellow.svg" />
</p>

# Tinyget

中文 | [English][003]

Tinyget 是一个 Python 的包管理工具，主要目的是封装各类包管理器的核心操作、提供虚拟接口，使得对它们的操作可以通过统一的接口和格式进行，减少各式各样的软件分发软件对用户造成的困扰。支持但不限于：apt、dnf、pacman 等。

<details>
  <summary> 🎬 演示视频 </summary>

&nbsp;

<a href="https://asciinema.org/a/zxl8AIYaSZIdgDHudjLzuaqH0" target="_blank"><img src="https://asciinema.org/a/zxl8AIYaSZIdgDHudjLzuaqH0.svg" /></a>

</details>

## 功能

- [x] 封装多种包管理器常用的软件操作，如安装、卸载、历史记录查看、回滚（目前只支持部分）、搜索、全局更新。
- [x] 常用的软件源配置。若你想要配置自己的软件源，请查看 [开发手册][001]。
- [x] 第三方软件包支持，让你可以下载普通包管理器无法自动下载的软件包。若你想配置自己的第三方软件，请查看 [开发手册][001]。
- [x] 支持 I18n，可在命令前加上 `LANG=en_US` 等切换语言。
- [x] 模拟提供接口。即使在 Ubuntu 下，你也可以使用 tinyget 提供的 dnf、pacman 等命令。我们会帮你模拟好等效的操作。
- [x] AI 自动纠正。打错了软件包名称或者命令？找 AI 帮你改。
- [ ] 自动更新。

## 快速上手

### 安装

```bash
pip install git+https://gitee.com/tinylab/tinyget.git
# 或者使用我们的特定开发版本
pip install git+https://gitee.com/tinylab/tinyget.git@ospp-2024
```

```bash
# 更新
pip install --upgrade git+https://gitee.com/tinylab/tinyget.git
```

### 使用方法

```bash
Usage: tinyget [OPTIONS] COMMAND [ARGS]...

Options:
  --config-path TEXT              Path to configuration file, default is
                                  ~/.config/tinyget/config.json
  --debug BOOLEAN                 Enable debug logs
  --live-output / --no-live-output
                                  Real-time stream output
  --host TEXT                     OpenAI host.
  --api-key TEXT                  OpenAI API key.
  --model TEXT                    OpenAI model.
  --max-tokens TEXT               OpenAI max tokens.
  --help                          Show this message and exit.

Commands:
  config          Interactively set up ai_helper for tinyget.
  history         check history
  install         Install packages.
  list            List packages.
  repo_configure  configure repo.
  repo_list       List all available repos in builtin mirror list.
  rollback        rollback to specified history
  search          Search package.
  server          TinyGet Server for GUI
  tui             TinyGet Simple TUI
  uninstall       Uninstall packages.
  update          Update the index of available packages.
  upgrade         Upgrade all available packages.
```

#### 基本操作

- `tinyget install` 安装软件包。
- `tinyget uninstall` 卸载软件包。
- `tinyget list` 列出可用的所有软件包。
- `tinyget search` 搜索软件包。
- `tinyget history` 查看本地包管理器操作历史记录。
- `tinyget repo_list` 查看可用软件源。
- `tinyget repo_configure` 配置选定的软件源。
- `tinyget rollback` 回滚操作。
- `tinyget update` 更新软件包检索。
- `tinyget upgrade` 全量更新。

#### 列包目录

```bash
tinyget list --help
Usage: tinyget list [OPTIONS]

  List packages.

Options:
  -I, --installed   Show only installed packages.
  -U, --upgradable  Show only upgradable packages.
  -C, --count       Show count of packages.
  --help            Show this message and exit.
```

#### 配置 AI 助手

本工具提供 AI 智能助手功能，当你的命令出现错误时，它会自动为你纠错。你可以通过 `config` 命令来配置 AI 助手。

```bash
Usage: tinyget config [OPTIONS]

  Interactively set up ai_helper for tinyget.

Options:
  -H, --host TEXT           openai api host, default is
                            https://api.openai.com, can be specified with
                            environment variable OPENAI_API_HOST
  -K, --api-key TEXT        openai api key, can be specified with environment
                            variable OPENAI_API_KEY
  -M, --model TEXT          model to use, can be specified with environment
                            variable OPENAI_MODEL
  -C, --max-tokens INTEGER  Maximum number of tokens to be generated, default
                            is 1024, can be specified with environment
                            variable OPENAI_MAX_TOKENS, 8192 is openai's max
                            value when using gpt-3.5-turbo
  -R, --repo-paths TEXT     Specify third-party softwares repo paths, default
                            will be softwares' repo/builtin dir. Can be
                            specified multiple times
  --help                    Show this message and exit.
```

#### TUI 界面

使用 `tinyget tui` 命令来启动 TUI 界面。

![tinyget_tui](images/tinyget_tui.png)

## 安全性声明

tinyget 默认调用系统包管理器以及官方包构建程序进行软件的更新、安装等操作，不额外调用其他可执行文件。

## 免责声明

对于第三方包中的商业软件，其知识产权归各商业公司拥有，tinyget 仅提供官方下载链接并都从该链接进行下载安装，原则上不做修改。

## 特别鸣谢

- [MirrorZ 项目][002]

## TODO List

- [ ] 在进行 `update` 操作时，若可用，自动更新第三方软件包的配置。
- [ ] 安装自检（tinyget --init/test）功能，测试安装后是否缺少依赖或者配置问题。
- [ ] 使用 async / multiprocessing 提升解析性能。
- [ ] 完善 rollback 功能。
- [ ] 自动发布。
- [ ] 提升 AI 助手使用体验。
- [ ] 同时提供 tinyget 本身的操作记录。
- [ ] 更多翻译语言支持。
- [ ] 提供类似 `rpm -ql` 功能列出软件包安装了哪些文件。

[001]: docs/Development.md
[002]: https://mirrorz.org
[003]: README_en.md
