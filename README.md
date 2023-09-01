# Tinyget

## 项目介绍

这是一个Python的包管理工具,目前处理两个主流的系统包管理器: `apt`(使用于Debian, Ubuntu等)和`dnf`(使用于Fedora, CentOS等)。这个库封装了各种包管理器的核心操作，使得对它们的操作可以通过统一的接口和格式进行。

## 类与函数

### 提供的接口类

在抽象类 `PackageManagerBase` 中定义了一份标准的包管理操作接口，所有的包管理类需要继承并实现此接口。接口包括以下方法：

- `list() -> List[Package]`：列出所有已安装的包。
- `update()`：更新软件包列表。
- `install(package: Package)`：安装一个软件包。
- `uninstall(package: Package)`：卸载一个软件包。
- `upgrade()`：升级所有已安装的软件包。
- `search(keyword, limit=10) -> List[Package]`：根据关键词搜索软件包。
- `get_package(package_name: str) -> Package`：获取关于一个软件包的详细信息。

### 数据类

- `PackageInfo` 类用于表示软件包的详细信息。
- `Package` 类用于表示一个软件包。

### 包管理器类

- `APT` 类用于对APT进行操作。
- `DNF` 类用于对DNF进行操作。

## 示例

以下是如何使用这个库的一个示例：

```python
if __name__ == "__main__":
    # 对于apt
    apt = APT()
    package = apt.get_package("curl")
    print(package)

    # 对于dnf
    dnf = DNF()
    packages = dnf.search("vim")
    package = packages[0]
    dnf.uninstall(package)
```

这个示例中，我们首先加载了 `apt` 和 `dnf`，然后获取了一个名为 "curl" 的软件包的信息并打印出来。然后，我们通过 `dnf` 查找了包含 "vim" 字样的所有软件包，并卸载了其中的第一个。

## 安装
```bash
pip3 install .
```

在 centos 系统中，python3-dnf 的功能由系统包提供，需要由如下指令安装，并且是必须在裸机环境下安装，不能使用 conda, virtualenv 等虚拟环境，否则会出现依赖问题。
```bash
dnf install python3-dnf
```