from .process import execute_command as _execute_command, CommandExecutionError
from .ai_helper import (
    AIHelper,
    AIHelperHostError,
    AIHelperKeyError,
    try_to_get_ai_helper,
)
from typing import Union, List
from rich.panel import Panel
from rich.console import Console
from rich.spinner import Spinner
import traceback
import click
import sys

ai_helper = try_to_get_ai_helper()


def execute_command(args: Union[List[str], str], envp: dict = {}, timeout: int = None):
    try:
        result = _execute_command(args, envp, timeout)
    except CommandExecutionError as e:
        console = Console()
        console.print(Panel(traceback.format_exc(), border_style="red", title="命令执行失败"))
        if ai_helper is None:
            console.print(
                Panel(
                    "AI助手没有启动，可以通过tinyget config或tinyget ui配置后启动",
                    border_style="bright_black",
                )
            )
        else:
            with console.status(
                "[bold green] AI助手已经激活，正在获取建议", spinner="bouncingBar"
            ) as status:
                recommendation = ai_helper.fix_command(args, e.stdout, e.stderr)
            console.print(
                Panel(
                    recommendation,
                    border_style="green",
                    title="来自AI助手的建议",
                )
            )
        sys.exit(0)
    except Exception:
        raise
    return result
