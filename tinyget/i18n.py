from gettext import translation
from tinyget.globals import global_configs
from tinyget.common_utils import logger
import os


def get_lang() -> str:
    if "LANG" not in os.environ:
        logger.warning(
            "Cannot find LANG environment variable, will use default language: en_US"
        )
        return "en_US"
    lang = os.environ["LANG"]
    lang = lang.split(".")[0]
    lpath = os.path.join(global_configs["LOCALE_DIR"], lang)  # type: ignore
    if not os.path.exists(lpath):
        logger.warning(
            f"Cannot find translation for {lang}, will use default language: en_US"
        )
        return "en_US"
    return lang


def load_translation(module: str):
    t = translation(
        module, localedir=global_configs["LOCALE_DIR"], languages=[get_lang()]  # type: ignore
    )
    return t.gettext
