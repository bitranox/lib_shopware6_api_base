# put Your imports here
# __init__conf__ needs to be imported after Your imports, otherwise we would create circular import on the cli script,
# which is reading some values from __init__conf__
from . import __init__conf__
from .conf_shopware6_api_base_classes import (
    ConfigurationError,
    load_config_from_env,
    require_config_from_env,
)
from .lib_shopware6_api_base import *
from .lib_shopware6_api_base_criteria import *

__title__ = __init__conf__.title
__version__ = __init__conf__.version
__name__ = __init__conf__.name
__url__ = __init__conf__.homepage
__author__ = __init__conf__.author
__author_email__ = __init__conf__.author_email
__shell_command__ = __init__conf__.shell_command
