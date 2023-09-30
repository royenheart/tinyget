#!/usr/bin/env python3
from .wrappers import PackageManager, package_manager_name
from typing import List
import click
import sys
import os


@click.group()
def cli():
    pass


@cli.command("list", help="List packages.")
@click.option(
    "--installed",
    "-I",
    is_flag=True,
    default=False,
    help="Show only installed packages.",
)
@click.option(
    "--upgradable",
    "-U",
    is_flag=True,
    default=False,
    help="Show only upgradable packages.",
)
@click.option(
    "--count", "-C", is_flag=True, default=False, help="Show count of packages."
)
def list_packages(installed: bool, upgradable: bool, count: bool):
    package_manager = PackageManager()
    packages = package_manager.list_packages(
        only_installed=installed, only_upgradable=upgradable
    )
    if count:
        click.echo(f"{len(packages)} packages in total.")
    else:
        for package in packages:
            click.echo(package)


@cli.command(help="Update the index of available packages.")
def update():
    package_manager = PackageManager()
    package_manager.update()


@cli.command(help="Upgrade all available packages.")
def upgrade():
    package_manager = PackageManager()
    package_manager.upgrade()


@cli.command(help="Install packages.")
@click.argument("package_names", nargs=-1, required=True)
def install(package_names: List[str]):
    package_manager = PackageManager()
    package_manager.install(package_names)


@cli.command(help="Uninstall packages.")
@click.argument("package_names", nargs=-1, required=True)
def uninstall(package_names: List[str]):
    package_manager = PackageManager()
    package_manager.uninstall(package_names)
