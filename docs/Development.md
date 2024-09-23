> Corrector: [TinyCorrect](https://gitee.com/tinylab/tinycorrect) v0.2-rc2 - [spaces toc urls pangu autocorrect]<br/>

# 开发手册

这里描述了 tinyget 软件的设计思路和主要结构，同时说明了如何为 tinyget 进行新功能的开发、处理潜在的 BUG。

## 技术路线

1. [hatchling python 项目管理工具][007]
2. [black 代码格式化工具][005]
3. [flake8 静态代码扫描工具][006]
4. [pytest 单元测试][002]
5. [click python 命令行界面工具包][004]
6. [rich python 富文本解析和美观输出][008]
7. [trogon 自动 TUI 生成器][009]
8. [gRPC 通信传输][010]

## Tinyget 项目结构

主要文件和模块：

- tinyget -- tinyget cli 源代码目录。
  - gui -- tinyget server 模块，充当 tinyget gui 的服务端
  - interact -- 底层交互模块，包括 AI 助手、subprocess 增强封装
  - locale -- 翻译文件存放位置
  - repos -- 第三方软件源，软件包配置模块
    - third_party.py -- 用于提供第三方软件源、软件包、仓库解析处理服务
    - builtin -- 内置仓库
      - mirrors -- 第三方镜像源配置
      - packages -- 第三方软件包配置
  - wrappers -- 包管理器封装模块
  - i18n.py -- I18n 配置
  - main.py -- 程序主入口
- .flake8 -- flake8 代码检查配置。
- hatch_build.py -- hatchling 构建的 Hook 脚本，用于判断系统版本、处理接口和依赖等。
- Makefile -- 提供自动配置开发环境、自动构建安装包和测试。
- pyproject.toml -- Python 项目配置文件。

## 如何进行开发

### 构建开发环境

Tinyget 需要支持多种操作系统和包管理器，为方便多端测试开发流程，Tinyget 推荐使用 VSCode IDE 进行开发，项目提供了 `.devcontainer` 文件夹放置 [VSCode Devcontainer][001] 配置文件，可在容器中开发测试。

要求 python 版本大于等于 3.8，执行 `pip install.` 安装或者在顶层目录执行 `make` 自动下载必要 python 软件、构建 tinyget 软件包和执行测试。

### 包管理器封装实现

在 `tinyget/wrappers/pkg_manager.py` 中定义了 `PackageManagerBase` 基类，当要添加新的包管理器时，在此模块下添加对应包管理器的封装模块并继承该基类实现对应的抽象接口，同时修改 hatchling 构建系统对模拟接口的识别以及在 `tinyget/wrappers/__init__.py` 中模块导入的判断逻辑即可：

```python
# tinyget/wrappers/__init__.py
if package_manager_name == "apt":
    from ._apt import APT as PackageManager

    MANAGER = ManagerType.apt
elif package_manager_name == "dnf":
    from ._dnf import DNF as PackageManager

    MANAGER = ManagerType.dnf
elif package_manager_name == "pacman":
    from ._pacman import PACMAN as PackageManager

    MANAGER = ManagerType.pacman
# elif package_manager_name == "Your Implemented Package Manager":
#   ......
else:
    raise NotImplementedError(f"Unsupported package manager: {package_manager_name}")
```

### 添加第三方软件包

tinyget 内置的第三方软件仓库位于 `tinyget/repos/builtin/packages` 下，你可以向社区发起 PR 合入自己的第三方软件配置，也可以安装后进入对应位置进行修改，tinyget 会在运行时动态导入（通过 python 的 importlib 模块）。当然，你也可以在 `tinyget` 配置文件中修改要进行搜索的软件仓库位置，目录结构和内置仓库相同即可，详细见 `tinyget config --help`。

这里以 QQ 为例，在 `packages/QQ` 目录下创建 `package.py` 文件，引入必要的 tinyget 模块并从 `third_party.py` 继承抽象基类 `ThirdPartySofts`，实现思路如下：

```python
# ......
from tinyget.package import ManagerType, Package
from tinyget.repos.third_party import ThirdPartySofts, download_file, AllPkgInfo
from tinyget.wrappers import MANAGER
from tinyget.globals import ARCH, SupportArchs
from tinyget.wrappers import PackageManager
from tinyget.common_utils import logger
# tinyget 会尽可能提供接口满足第三方软件安装需求，尽量只使用 python 原生接口和 tinyget 接口从，防止动态导入时无法使用未被安装的模块。
# 若需要的接口功能 tinyget 并没有实现，欢迎提出 issue 让我们知晓并去实现。

class _QQ(ThirdPartySofts):

    HOMEPAGE = "xxx"
    VERSION = "xxxx"
    DOWNLOAD_PAGE = "xxx"
    PKG_NAME = AllPkgInfo.LINUXQQ

    @property
    def is_support(self) -> bool:
        # xxx，判断 QQ 在当前系统下是否支持。对于 QQ，需要查看官网提供的安装包，并编写对应的逻辑。
        if (
            (MANAGER == ManagerType.dnf and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.dnf and ARCH == SupportArchs.x86_64)
            # ......
        ):
            return True
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.x86_64:
            return True
        # elif ......
        else:
            return False

    def url(self) -> Optional[str]:
        # 因为 QQ 没有提供软件源，只能从官网下载得到安装包，然后进行安装
        # 由于嵌入到了各个包管理器封装的搜索逻辑中，只要包管理器支持本地安装，那么直接提供下载的安装包位置就可以进行安装
        # 可以使用 tinyget 提供的 download_file 或者包管理器的 build 服务下载或者构建软件包。
        tmpdir = tempfile.mkdtemp()
        if (
            (MANAGER == ManagerType.dnf and ARCH == SupportArchs.arm64)
            or (MANAGER == ManagerType.dnf and ARCH == SupportArchs.x86_64)
            # ......
        ):
            n = f"{_QQ.PKG_NAME}_{_QQ.VERSION.replace('_', '-')}_{ARCH}.{MANAGER.ext}"
            url = f"{_QQ.DOWNLOAD_PAGE}/{n}"
            downloads = os.path.join(tmpdir, n)
            download_file(url=url, output_file=downloads)
            return downloads
        elif MANAGER == ManagerType.apt and ARCH == SupportArchs.x86_64:
            # pacman 需要额外进行构建
            return pacman.build(folder=tmpdir)
        # elif ......
        else:
            return None

    def get_pkg_url(self) -> Optional[str]:
        return self.url()

    def get_package(
        self, wrapper_softs: Optional[List[Package]] = []
    ) -> Optional[Package]:
        if not self.is_support:
            return None

        # 和普通包管理器得到的软件列别进行对比，更新软件包信息
        if wrapper_softs is not None:
            for p in wrapper_softs:
                if p.package_name == _QQ.PKG_NAME and p.installed is True:
                    # ......

        return Package(
            package_type=MANAGER,
            package_name=_QQ.PKG_NAME,
            # ......
        )
```

添加完成后若有向 tinyget 提出 PR 合入配置的需求，请在 `tinyget/repos/third_party.py` 中的 `AllPkgInfo` 组中注册你的软件包信息：

```python
@unique
class AllPkgInfo(str, Enum):
    LINUXQQ = "linuxqq"
    # YouPackageEnumName = "YourPackageName"
```

在实现基类时，使用 AllPkgInfo Enum 结构标识你的类（目前使用 `PKG_NAME = AllPkgInfo.LINUXQQ` 的方式）。这样的目的是提升安全性，我们可能在后续的更新中会加强这一方面的检测，防止恶意软件包的植入。

### 添加软件源配置

软件源的配置方式相比第三方软件最大的不同是相当自由，不像第三方软件很多时候只需要安装包和包管理器的介入。同时现有包管理器修改软件源的方式仍是直接修改配置文件而没有提供对应的 CLI 接口（或者并不完善）。出于安全性考虑，tinyget 目前只实现在临时目录下生成配置脚本，让用户自行评估并运行。

tinyget 内置的软件源仓库位于 `tinyget/repos/builtin/mirrors/templates` 下，贡献和配置文件编写方式和第三方软件包类似。这里以 LLVM APT 为例。LLVM APT 是针对 LLVM 软件提供的 apt 软件源，我们在 `templates` 目录下提供了对应的 `llvm_apt.py` 配置文件，也需要实现抽象基类 `ThirdPartySofts`：

```python
# ......
from tinyget.repos.third_party import (
    AllMirrorInfo,
    AllSystemInfo,
    ThirdPartyMirrors,
    ask_for_mirror_options,
    get_os_version,
    judge_os_in_systemlist,
)
from tinyget.common_utils import logger, strip_str_lines

class _llvm(ThirdPartyMirrors):
    MIRROR_NAME = AllMirrorInfo.LLVM_APT

    def get_template(self) -> Optional[str]:
        # 通过 tinyget 提供的接口判断是否符合对应系统需求
        oinfo = get_os_version()
        if not judge_os_in_systemlist(
            oinfo,
            [
                AllSystemInfo.DEBIAN_BOOKWORM,
                AllSystemInfo.DEBIAN_BULLSEYE,
                AllSystemInfo.UBUNTU_JAMMY,
                AllSystemInfo.UBUNTU_FOCAL,
                AllSystemInfo.UBUNTU_BIONIC,
            ],
        )[0]:
            logger.warning(f"LLVM APT does not support os {oinfo}")
            return None
        _, _, os_codename = oinfo
        OS_VERSION = os_codename
        # 一些额外的配置选项，用问答的形式交由用户填写输入
        w = ask_for_mirror_options(
            options={
                ("llvm", "Use what LLVM version"): [
                    "default",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                ]
            },
            true_or_false=[
                ("use_scripts", "Use scripts to atomatically install llvm?"),
                ("use_source_mirror", "Enable source mirror?"),
            ],
        )
        # 根据用户输入配置脚本控制参数
        USE_SCRIPTS = False
        for qa in w:
            q, a = qa
            if q == "use_scripts":
                USE_SCRIPTS = bool(a)
            # elif ......
        # 生成脚本内容
        TEMPLATE = (
            f"""#!/bin/bash
# {USE_SCRIPTS} ......
# ........."""
        )
        return strip_str_lines(TEMPLATE)
```

添加完成后若有向 tinyget 提出 PR 合入配置的需求，请在 `tinyget/repos/third_party.py` 中的 `AllMirrorInfo` 组中注册你的软件包信息，这样做的目的同样是为了安全性：

```python
@unique
class AllMirrorInfo(str, Enum):
    UBUNTU = "ubuntu"
    LLVM_APT = "llvm_apt"
    DEBIAN = "debian"
    ARCHLINUX = "archlinux"
    # YouMirrorEnumName = "YourMirrorName"
```

### 编写 I18n

- [gettext 开发和使用教程参考 1][012]
- [gettext 开发和使用教程参考 2][011]

使用 python 自带的 gettext 进行 I18n。翻译文件位于 `tinyget/locale` 目录下，gettext 简易使用命令可以参考该目录下的 [README][014]。

需要注意通过 gettext 生成的二进制文件目前同样纳入了版本控制，在后续版本中可能会交由 hatchling 构建系统来在安装、打包时自动生成。

目前推荐在修改了翻译的文本文件（.po 文件）后，使用该目录下的 [`generate.sh`][013] 自动生成翻译文件并计算哈希值。同样在二进制翻译文件不再纳入版本更新后该脚本可能会被去除。

### 文档编写

推荐使用 [tinycorrect][003] 自动规范文档。

## 代码片段解释

对一些代码片段进行解释，方便开发者在后续遇到对应的 BUG 或潜在的性能优化机会时更快速地定位和分析。

### 高级命令调用系统实现

由于 tinyget 以 subprocess + 命令行解析的形式封装包管理器功能，而原生的 subprocess 库要么没法实时输出结果，要么限定了输入（通过 communicate 的 input 参数设置输入）。在执行包管理器命令过程中可能会要求用户输入，比如选择是否继续安装软件包、是否解决依赖冲突等等。为了让用户有选择的余地而不是完全忽略这些输入使用偷懒的 `--noconfirm` 等参数，tinyget 需要有实时的输入输出，同时也能在程序结束后获取最终的输出、状态返回码以进行文本解析。

为此，tinyget 基于 subprocess、async 异步操作、threading、termios 终端以及 select 事件监听技术实现了更高级的命令调用系统。这部分代码位于 `tinyget/interact/process.py` 中，主要为：

1. spawn 函数，封装 subprocess 命令，用于生成 subprocess 进程。
2. async_execute_command 函数，异步解析侦测 subprocess 进程，提供实时的标准输出、错误输出以及输入。
3. run_event_loop_in_thread 函数，创建新的线程和对应的 asyncio loop 专门进行协程的处理，可以被复用到其他需要 async 异步的操作，分离出主线程而不是直接调用 `asyncio.run()`。
4. execute_command 函数，subprocess 上层封装，执行命令时调用该函数即可。
5. non_blocking_input 函数，非阻塞输入读取，使用了 select 事件监听机制和 asyncio event loop 提供的超时退出功能，使得操作完成后能正常推出而不是仍在阻塞运行。
6. read_subprocess_output 函数，异步读取标准输出。
7. read_subprocess_err 函数，异步读取标准错误。
8. read_input 函数，non_blocking_input 封装，异步读取输入。

执行流程和结构如下所示：

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                         ┌─────────┐ │
│                                                         │select   │ │
│                                                         │input    │ │
│                      ┌─────────────────────────┐        └─┬───────┘ │
│                      │                         │          │         │
│                      │          ┌─────────┐ ┌──┴──────┐ ┌─▼───────┐ │
│                      │          │read sub │ │read sub │ │read     │ │
│                      │   ┌──────┼process  │ │process  │ │input    │ │
│                      │   │      │output   │ │err      │ │         │ │
│  ┌───────────────────▼───▼─┐    │         │ │         │ │         │ │
│  │Async execute command    │    └─────▲───┘ └────▲────┘ └─────▲───┘ │
│  │                         │          │          │            │     │
│  │Async output / Async err │    ┌─────┴──────────┴────────────┴───┐ │
│  │                         │    │Thread pool executor             │ │
│  └────────────────────────▲┘    │                                 │ │
│                           │     └─────────▲───────────────────────┘ │
│                      ┌────┴───────────────┴────┐                    │
│                      │AsyncIO                  │                    │
│                      └▲───────────────────▲────┘                    │
│                  ┌────┴───────────────────┴────────┐                │
│   ┌──────────┐   │                                 │                │
│   │          │   │  run event loop in thread       │                │
│   │ spawn    │   │                                 │                │
│   │          │   │                       New Thread│                │
│   └──┬───────┘   └──────────────▲──────────────────┘                │
│      │                          │                                   │
│      │                          │                                   │
│   ┌──▼──────────────────────────┴──────────────────┐                │
│   │                                                │                │
│   │    execute_command                             │                │
│   │                                                │                │
│   └────────────────────────────────────────────────┘                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 模拟提供包管理器 CLI 接口

该部分基于 hatchling 构建系统的动态 hook 功能实现，具体代码实现在根目录的 `hatch_build.py` 以及 `tinyget/wrappers/__init__.py` 文件中实现。

具体实现思路是使用 `click` 库的 `group` 为每一个包管理器生成对应的命令组，同时在提供的 `Package manager` 抽象接口的基础上尽可能模拟对应包管理器的参数格式和功能（实际调用的仍然是当前系统上可用的包管理器）。`hatch_build.py` 会在 hatchling 打包时 hook 并修改项目描述文件（`pyproject.toml`）中有关应用入口的元数据：

```python
simulate_managers = {
    "apt": "tinyget.wrappers:sim_apt",
    "dnf": "tinyget.wrappers:sim_dnf",
    "pacman": "tinyget.wrappers:sim_pacman",
}

if current_package_manager == "apt":
    simulate_managers.pop("apt")
elif current_package_manager == "dnf":
    simulate_managers.pop("dnf")
elif current_package_manager == "pacman":
    simulate_managers.pop("pacman")

metadata["scripts"] = {"tinyget": "tinyget.main:cli"}
metadata["scripts"].update(simulate_managers)
```

current_package_manager 根据系统版本（主要通过标准的 `/etc/os-release` 文件）决定，比如使用 dnf 包管理器的 fedora 系统便会生成 `apt` 和 `pacman` 的模拟接口，实现模拟提供包管理器 CLI 接口的功能。

[001]: https://code.visualstudio.com/docs/devcontainers/containers
[002]: https://docs.pytest.org/en/stable/
[003]: https://gitee.com/tinylab/tinycorrect
[004]: https://github.com/pallets/click
[005]: https://github.com/psf/black
[006]: https://github.com/PyCQA/flake8
[007]: https://github.com/pypa/hatch
[008]: https://github.com/Textualize/rich
[009]: https://github.com/Textualize/trogon
[010]: https://grpc.io/
[011]: https://lokalise.com/blog/translating-apps-with-gettext-comprehensive-tutorial/
[012]: https://phrase.com/blog/posts/translate-python-gnu-gettext/
[013]: ../tinyget/locale/generate.sh
[014]: ../tinyget/locale/README.md
