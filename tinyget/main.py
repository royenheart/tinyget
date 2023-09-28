#!/usr/bin/env python3
from .wrappers import PackageManager
import click
import sys


@click.group()
def cli():
    pass


@cli.command()
@click.option("--only-installed", is_flag=True, default=True)
def list(only_installed: bool):
    package_manager = PackageManager()
    packages = package_manager.list_packages(only_installed=only_installed)
    for package in packages:
        click.echo(package)
