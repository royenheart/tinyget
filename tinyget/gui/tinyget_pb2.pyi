from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SoftsResquest(_message.Message):
    __slots__ = ("pkgs", "only_installed", "only_upgradable")
    PKGS_FIELD_NUMBER: _ClassVar[int]
    ONLY_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    ONLY_UPGRADABLE_FIELD_NUMBER: _ClassVar[int]
    pkgs: str
    only_installed: bool
    only_upgradable: bool
    def __init__(self, pkgs: _Optional[str] = ..., only_installed: bool = ..., only_upgradable: bool = ...) -> None: ...

class SoftsInstallRequests(_message.Message):
    __slots__ = ("pkgs",)
    PKGS_FIELD_NUMBER: _ClassVar[int]
    pkgs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, pkgs: _Optional[_Iterable[str]] = ...) -> None: ...

class SoftsUninstallRequests(_message.Message):
    __slots__ = ("pkgs",)
    PKGS_FIELD_NUMBER: _ClassVar[int]
    pkgs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, pkgs: _Optional[_Iterable[str]] = ...) -> None: ...

class SysUpdateRequest(_message.Message):
    __slots__ = ("upgrade",)
    UPGRADE_FIELD_NUMBER: _ClassVar[int]
    upgrade: bool
    def __init__(self, upgrade: bool = ...) -> None: ...

class SysHistoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Package(_message.Message):
    __slots__ = ("package_name", "architecture", "description", "version", "installed", "automatically_installed", "upgradable", "available_version", "repo")
    PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    ARCHITECTURE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INSTALLED_FIELD_NUMBER: _ClassVar[int]
    AUTOMATICALLY_INSTALLED_FIELD_NUMBER: _ClassVar[int]
    UPGRADABLE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_VERSION_FIELD_NUMBER: _ClassVar[int]
    REPO_FIELD_NUMBER: _ClassVar[int]
    package_name: str
    architecture: str
    description: str
    version: str
    installed: bool
    automatically_installed: bool
    upgradable: bool
    available_version: str
    repo: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, package_name: _Optional[str] = ..., architecture: _Optional[str] = ..., description: _Optional[str] = ..., version: _Optional[str] = ..., installed: bool = ..., automatically_installed: bool = ..., upgradable: bool = ..., available_version: _Optional[str] = ..., repo: _Optional[_Iterable[str]] = ...) -> None: ...

class History(_message.Message):
    __slots__ = ("id", "command", "date", "operations")
    ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    OPERATIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    command: str
    date: str
    operations: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., command: _Optional[str] = ..., date: _Optional[str] = ..., operations: _Optional[_Iterable[str]] = ...) -> None: ...

class SoftsResp(_message.Message):
    __slots__ = ("softs",)
    SOFTS_FIELD_NUMBER: _ClassVar[int]
    softs: _containers.RepeatedCompositeFieldContainer[Package]
    def __init__(self, softs: _Optional[_Iterable[_Union[Package, _Mapping]]] = ...) -> None: ...

class SysHistoryResp(_message.Message):
    __slots__ = ("histories",)
    HISTORIES_FIELD_NUMBER: _ClassVar[int]
    histories: _containers.RepeatedCompositeFieldContainer[History]
    def __init__(self, histories: _Optional[_Iterable[_Union[History, _Mapping]]] = ...) -> None: ...

class SoftsInstallResp(_message.Message):
    __slots__ = ("retcode", "stdout", "stderr")
    RETCODE_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    retcode: int
    stdout: str
    stderr: str
    def __init__(self, retcode: _Optional[int] = ..., stdout: _Optional[str] = ..., stderr: _Optional[str] = ...) -> None: ...

class SoftsUninstallResp(_message.Message):
    __slots__ = ("retcode", "stdout", "stderr")
    RETCODE_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    retcode: int
    stdout: str
    stderr: str
    def __init__(self, retcode: _Optional[int] = ..., stdout: _Optional[str] = ..., stderr: _Optional[str] = ...) -> None: ...

class SysUpdateResp(_message.Message):
    __slots__ = ("retcode", "stdout", "stderr")
    RETCODE_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    retcode: int
    stdout: str
    stderr: str
    def __init__(self, retcode: _Optional[int] = ..., stdout: _Optional[str] = ..., stderr: _Optional[str] = ...) -> None: ...
