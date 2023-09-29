#!/usr/bin/env python3
from .wrappers import PackageManager
import click
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.option("--installed", is_flag=True, default=False)
@click.option("--upgradable", is_flag=True, default=False)
def list(installed: bool, upgradable: bool):
    package_manager = PackageManager()
    packages = package_manager.list_packages(
        only_installed=installed, only_upgradable=upgradable
    )
    for package in packages:
        click.echo(package)
