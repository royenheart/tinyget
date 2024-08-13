#!/usr/bin/env python3
from .wrappers import PackageManager
from .interact import AIHelper, AIHelperHostError, AIHelperKeyError
from .common_utils import set_configuration, setup_logger
from .globals import global_configs

from typing import List
from trogon import tui
import click


@tui(command="ui", help="TinyGet UI")
@click.group()
@click.option(
    "--config-path",
    default=None,
    help="Path to configuration file, default is ~/.config/tinyget/config.json",
)
@click.option("--debug", default=False, help="Enable debug logs")
@click.option("--host", default=None, help="OpenAI host.")
@click.option("--api-key", default=None, help="OpenAI API key.")
@click.option("--model", default=None, help="OpenAI model.")
@click.option("--max-tokens", default=None, help="OpenAI max tokens.")
def cli(
    config_path: str, debug: bool, host: str, api_key: str, model: str, max_tokens: int
):
    global_configs["config_path"] = config_path
    global_configs["host"] = host
    global_configs["api_key"] = api_key
    global_configs["model"] = model
    global_configs["max_tokens"] = max_tokens
    setup_logger(debug=debug)


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


@cli.command(help="Search package.")
@click.argument("package", nargs=1, required=True)
def search(package: str):
    package_manager = PackageManager()
    package_manager.search(package)


@cli.command(help="Interactively set up ai_helper for tinyget.")
@click.option(
    "--host",
    "-H",
    default="https://api.openai.com",
    help="openai api host, default is https://api.openai.com, can be specified with environment variable OPENAI_API_HOST",
)
@click.option(
    "--api-key",
    "-K",
    default=None,
    help="openai api key, can be specified with environment variable OPENAI_API_KEY",
)
@click.option(
    "--model",
    "-M",
    default="gpt-3.5-turbo",
    help="model to use, can be specified with environment variable OPENAI_MODEL",
)
@click.option(
    "--max-tokens",
    "-C",
    default=1024,
    help="Maximum number of tokens to be generated, default is 1024, can be specified with environment variable OPENAI_MAX_TOKENS, 8192 is openai's max value when using gpt-3.5-turbo",
)
def config(host: str, api_key: str, model: str, max_tokens: int):
    if all([v is not None for v in [host, api_key, model, max_tokens]]):
        ai_helper = AIHelper(
            host=host, api_key=api_key, model=model, max_tokens=max_tokens
        )
        config_valid = True
        try:
            ai_helper.check_config()
        except AIHelperHostError as e:
            click.echo(f"Host error: {e.host}")
            config_valid = False
        except AIHelperKeyError as e:
            click.echo(f"Key error: {e.key}")
            config_valid = False
        except Exception:
            raise

        if config_valid and not ai_helper.model_available():
            click.echo(f"Model {model} is not available.")
            config_valid = False

        if not config_valid:
            click.confirm(
                "Some configuration is invalid, still want to save?", abort=True
            )
        set_configuration(path=global_configs["config_path"], conf=ai_helper.config())
    else:
        click.confirm(
            "Not all configuration is specified, still want to save?", abort=True
        )
        ai_helper = AIHelper(
            host=host, api_key=api_key, model=model, max_tokens=max_tokens
        )
        set_configuration(path=global_configs["config_path"], conf=ai_helper.config())
