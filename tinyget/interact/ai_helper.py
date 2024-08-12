import json
import requests
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse

from ..common_utils import get_configuration_with_environ
from ..globals import global_configs

SYSTEM_PROMPT = """
你是一个熟练的Linux专家，精通各类发行版中的包管理器，也能熟练运用各类软件包管理器的命令。
用户将会告诉你他执行的命令、命令的stdout、命令的stderr。
你帮助用户对当前错误进行解释，并给出建议使用的命令。注意，建议使用的命令应该严格遵循markdown语法。
"""


class ModelException(Exception):
    def __init__(self, message, model, response):
        """
        Initializes a new instance of the MyClass class.

        Args:
            message (str): The message to be passed to the superclass constructor.
            model: The model to be assigned to the `model` attribute.
            response: The response to be assigned to the `response` attribute.
        """
        super().__init__(message)
        self.model = model
        self.reponse = response


class AIHelperHostError(Exception):
    def __init__(self, message, host):
        """
        Initializes a new instance of the class.

        Args:
            message (str): The message for the exception.
            host (str): The host information.

        Returns:
            None
        """
        super().__init__(message)
        self.host = host


class AIHelperKeyError(Exception):
    def __init__(self, message, host, key, response):
        """
        Initializes a new instance of the class.

        Args:
            message (str): The message to display.
            host (str): The host to connect to.
            key (str): The key to use for authentication.
            response (str): The response to expect.

        Returns:
            None
        """
        super().__init__(message)
        self.host = host
        self.key = key
        self.response = response


def do_completion(
    host: str,
    model: str,
    api_key: str,
    temperature: float,
    messages: List[Dict[str, str]],
    max_tokens: int,
) -> Dict:
    """
    Perform completion using the OpenAI GPT-3 model.

    Args:
        host (str): The host URL where the completion API is located.
        model (str): The name or ID of the model to be used for completion.
        api_key (str): The API key for authentication.
        temperature (float): The temperature parameter for controlling the randomness of the completion.
        messages (List[Dict[str, str]]): A list of messages containing user and assistant inputs.
        max_tokens (int): The maximum number of tokens in the completion response.

    Returns:
        str: The completion response from the API.

    Raises:
        None
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    url = urljoin(host, "v1/chat/completions")
    content = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(headers=headers, url=url, json=content)
    res = json.loads(response.content.decode())
    return res


class AIHelper:
    def __init__(
        self,
        host: str,
        api_key: str,
        model: Optional[str] = None,
        max_tokens: int = 1024,
    ):
        """
        Initializes the class instance with the provided parameters.

        Args:
            host (str): The host URL of the API.
            api_key (str): The API key for authentication.
            model (str, optional): The model to be used for processing. Defaults to None.
            max_tokens (int, optional): The maximum number of tokens to be generated. Defaults to 1024.

        Returns:
            None
        """
        scheme = urlparse(host).scheme
        if not scheme:
            host = f"https://{host}"
        self.host = host
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens

    def config(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "api_key": self.api_key,
            "model": self.model,
            "max_tokens": self.max_tokens,
        }

    def list_models(self) -> bool:
        """
        Retrieves a list of models from the server.

        :return: A boolean value indicating the success of the request.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        url = urljoin(self.host, "v1/models")
        response = requests.get(headers=headers, url=url)
        res = json.loads(response.content.decode())["data"]
        return res

    def check_config(self):
        """
        Checks the validity of the API key and host by sending a GET request to the server and verifying the response.

        This function does not take any parameters.

        Returns:
            None

        Raises:
            AIHelperHostError: If the host is invalid.
            AIHelperKeyError: If the API key is invalid.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        url = urljoin(self.host, "v1/models")
        try:
            response = requests.get(headers=headers, url=url)
        except Exception:
            raise AIHelperHostError("Invalid host", self.host)
        try:
            res = json.loads(response.content.decode())["data"]
        except Exception:
            raise AIHelperKeyError("Invalid key", self.host, self.api_key, response)

    def model_available(self, model: Optional[str] = None) -> bool:
        """
        Check if a model is available.

        Args:
            model (str): The name of the model to check availability for.

        Returns:
            bool: True if the model is available, False otherwise.

        Raises:
            ModelException: If the model returns an unexpected response.
        """
        if model is None:
            model = self.model
        if model is None:
            raise Exception("Please specify a model name.")
        messages = [{"role": "user", "content": "1"}]
        result = do_completion(
            host=self.host,
            model=model,
            api_key=self.api_key,
            temperature=0.0,
            max_tokens=2,
            messages=messages,
        )
        if "error" in result:
            return False
        elif "choices" in result:
            return True
        else:
            raise ModelException("Model returned an unexpected response", model, result)

    def ok(self) -> bool:
        try:
            self.check_config()
        except AIHelperHostError:
            return False
        except AIHelperKeyError:
            return False

        return self.model_available()

    def ask(self, query: str) -> str:
        """
        Executes a question by generating a completion based on the provided query.

        Args:
            query (str): The question or query to be asked.

        Returns:
            str: The generated completion as the answer to the question.

        Raises:
            Exception: If no model name is specified before asking a question.
        """
        if self.model is None:
            raise Exception("Please specify a model name before asking a question.")
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        result = do_completion(
            host=self.host,
            model=self.model,
            api_key=self.api_key,
            temperature=0.0,
            max_tokens=self.max_tokens,
            messages=messages,
        )
        answer = result["choices"][0]["message"]["content"]
        return answer

    def fix_command(
        self,
        command: Union[List[str], str],
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ) -> str:
        """
        Executes a command and returns the answer obtained from asking a question based on the command, stdout, and stderr.

        Parameters:
            command (Union[List[str], str]): The command to be executed. It can be passed as a list of strings or as a single string.
            stdout (str): The standard output obtained from executing the command (default is None).
            stderr (str): The standard error obtained from executing the command (default is None).

        Returns:
            str: The answer obtained from asking a question based on the command, stdout, and stderr.
        """
        if isinstance(command, list):
            command = " ".join(command)

        question = f"""
        我执行的命令是：
        ```bash
        {command}
        ```"""

        if stdout is not None:
            question += f"""
            我得到的stdout是：
            ```
            {stdout}
            ```"""

        if stderr is not None:
            question += f"""
            我得到的stderr是：
            ```
            {stderr}
            ```"""
        answer = self.ask(question)
        return answer


def try_to_get_ai_helper():
    configs = get_configuration_with_environ(
        path=global_configs.get("config_path"),
        key_environ={
            "host": "OPENAI_API_HOST",
            "api_key": "OPENAI_API_KEY",
            "model": "DEFAULT_MODEL",
            "max_tokens": "MAX_TOKENS",
        },
    )

    if not all(val is not None for val in configs.values()):
        return None

    ai_helper = AIHelper(
        host=configs["host"],
        api_key=configs["api_key"],
        model=configs["model"],
        max_tokens=configs["max_tokens"],
    )
    if ai_helper.ok():
        return ai_helper
    else:
        return None


if __name__ == "__main__":
    ai_helper = try_to_get_ai_helper()
    print(ai_helper)
