from typing import Optional
from tinyget.common_utils import logger
from concurrent import futures
from tinyget.wrappers import PackageManager
import asyncio
import click
import tinyget.gui.tinyget_pb2 as tinygetlib
import tinyget.gui.tinyget_pb2_grpc as tinygetgrpc
import grpc


class TinygetServer:
    class TinygetService(tinygetgrpc.TinygetGRPCServicer):
        def __init__(self, outer: "TinygetServer") -> None:
            self._outer = outer
            self._cached_list_softwares = {}
            self._lock = asyncio.Lock()
            self._pkg_manager = PackageManager()
            super().__init__()

        async def _get_softs(
            self,
            only_installed: bool,
            only_upgradable: bool,
            pkgs: Optional[str] = None,
        ):
            await self._lock.acquire()
            try:
                click.echo(f"Start get softwares: {pkgs if pkgs else ''}")
                h = (only_installed, only_upgradable, pkgs)
                if h in self._cached_list_softwares:
                    sh = self._cached_list_softwares[h]
                    click.echo(f"Get {len(sh)} softwares")
                    return sh
                if pkgs is not None and pkgs != "":
                    # search for certain packages
                    packages = self._pkg_manager.search(pkgs)
                else:
                    # list all packages
                    packages = self._pkg_manager.list_packages(
                        only_installed=only_installed,
                        only_upgradable=only_upgradable,
                    )
                click.echo(f"Get {len(packages)} softwares")
                self._cached_list_softwares[h] = packages
            finally:
                self._lock.release()
            return packages

        async def SoftsGet(self, request: tinygetlib.SoftsResquest, context):
            pkgs = []
            packages = await self._get_softs(
                request.only_installed, request.only_upgradable, request.pkgs
            )
            for package in packages:
                pkgs.append(
                    tinygetlib.Package(
                        package_name=package.package_name,
                        architecture=package.architecture,
                        description=package.description,
                        version=package.version,
                        installed=package.installed,
                        automatically_installed=package.automatically_installed,
                        upgradable=package.upgradable,
                        available_version=package.available_version,
                        repo=package.remain["repo"],
                    )
                )
            return tinygetlib.SoftsResp(softs=pkgs)

        async def SoftsGetStream(self, request: tinygetlib.SoftsResquest, context):
            packages = await self._get_softs(
                request.only_installed, request.only_upgradable, request.pkgs
            )
            for package in packages:
                yield tinygetlib.Package(
                    package_name=package.package_name,
                    architecture=package.architecture,
                    description=package.description,
                    version=package.version,
                    installed=package.installed,
                    automatically_installed=package.automatically_installed,
                    upgradable=package.upgradable,
                    available_version=package.available_version,
                    repo=package.remain["repo"],
                )

        async def SoftsInstall(self, request: tinygetlib.SoftsInstallRequests, context):
            pkgs = []
            for pkg in request.pkgs:
                pkgs.append(pkg)
            await self._lock.acquire()
            try:
                click.echo(f"Start install softwares: {pkgs if len(pkgs) > 0 else ''}")
                out, err, retcode = self._pkg_manager.install(pkgs)
                self._cached_list_softwares.clear()
                click.echo(f"Output: {out}\nErr: {err}\nRetcode: {retcode}")
            finally:
                self._lock.release()
            return tinygetlib.SoftsInstallResp(retcode=retcode, stdout=out, stderr=err)

        async def SoftsUninstall(
            self, request: tinygetlib.SoftsUninstallRequests, context
        ):
            pkgs = []
            for pkg in request.pkgs:
                pkgs.append(pkg)
            await self._lock.acquire()
            try:
                click.echo(
                    f"Start uninstall softwares: {pkgs if len(pkgs) > 0 else ''}"
                )
                out, err, retcode = self._pkg_manager.uninstall(pkgs)
                self._cached_list_softwares.clear()
                click.echo(f"Output: {out}\nErr: {err}\nRetcode: {retcode}")
            finally:
                self._lock.release()
            return tinygetlib.SoftsUninstallResp(
                retcode=retcode, stdout=out, stderr=err
            )

        async def SysUpdate(self, request: tinygetlib.SysUpdateRequest, context):
            await self._lock.acquire()
            try:
                if request.upgrade:
                    click.echo("Start system upgrade")
                    out, err, retcode = self._pkg_manager.upgrade()
                else:
                    click.echo("Start system update")
                    out, err, retcode = self._pkg_manager.update()
                self._cached_list_softwares.clear()
                click.echo(f"Output: {out}\nErr: {err}\nRetcode: {retcode}")
            finally:
                self._lock.release()
            return tinygetlib.SysUpdateResp(retcode=retcode, stdout=out, stderr=err)

        async def SysHistory(self, request: tinygetlib.SysHistoryRequest, context):
            await self._lock.acquire()
            try:
                click.echo("Get system pkg manage histories")
                histories = self._pkg_manager.history()
                click.echo(f"Collected {len(histories)} histories")
            finally:
                self._lock.release()
            hists = []
            for his in histories:
                hists.append(
                    tinygetlib.History(
                        id=his.id,
                        command=his.command,
                        date=str(his.date),
                        operations=his.operations,
                    )
                )
            return tinygetlib.SysHistoryResp(histories=hists)

        async def SysHistoryStream(
            self, request: tinygetlib.SysHistoryRequest, context
        ):
            await self._lock.acquire()
            try:
                click.echo("Get system pkg manage histories")
                histories = self._pkg_manager.history()
                click.echo(f"Collected {len(histories)} histories")
            finally:
                self._lock.release()
            for his in histories:
                yield tinygetlib.History(
                    id=his.id,
                    command=his.command,
                    date=str(his.date),
                    operations=his.operations,
                )

    def __init__(
        self,
        port: Optional[int] = 5051,
        address: Optional[str] = "[::]",
    ) -> None:
        self._port = port
        self._address = address

    async def serve(self) -> None:
        binding = f"{self._address}:{self._port}"
        server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=3))
        tinyget_service = self.TinygetService(self)
        tinygetgrpc.add_TinygetGRPCServicer_to_server(tinyget_service, server)
        server.add_insecure_port(binding)
        await server.start()
        logger.info(f"Server started, listening on {binding}")

        try:
            await server.wait_for_termination()
        except KeyboardInterrupt as e:
            logger.info("Server stop")
            await server.stop(5)
