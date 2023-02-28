import os
import os.path
import sys
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, Iterator, List, Optional, Union

from . import hooks, log, util


g_conf: Optional['Config'] = None
ConfigDict = Dict[str, Any]
DEFAULT_PELCONF_NAME = 'peltak.yaml'
PELTAK_CONFIG_FILES = frozenset({'peltak.yaml', 'pelconf.yaml', 'pyproject.toml'})


class ConfigError(RuntimeError):
    pass


class ConfigNotInitialized(ConfigError):
    pass


class ConfigAlreadyInitialized(ConfigError):
    pass


def init():
    global g_conf

    if g_conf is not None:
        # Running init() multiple times should have no effect.
        return

    config_path = _discover_proj_config()
    g_conf = _load_config(config_path)

    hooks.register.call('post-conf-load')


def get(name: str, *default: Any) -> Any:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    return g_conf.get(name, *default)


def get_path(name: str, *default: Any) -> Any:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    return g_conf.get_path(name, *default)


def get_env(name: str, *default: Any) -> Union[str, Any]:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    return g_conf.get_env(name, *default)


def proj_path(*path_parts: str) -> str:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    return g_conf.proj_path(*path_parts)


def as_dict() -> ConfigDict:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    return g_conf.values.get('cfg', {})


@contextmanager
def within_proj_dir(path: str = '.') -> Iterator[None]:
    global g_conf

    if not g_conf:
        raise ConfigNotInitialized()

    curr_dir = os.getcwd()

    os.chdir(g_conf.proj_path(path))
    yield
    os.chdir(curr_dir)


class Config:
    """ Represents the `pelconf.yaml` file. """
    def __init__(
        self,
        values: Optional[ConfigDict] = None,
        *,
        path: Optional[str] = None,
    ):
        self.values: ConfigDict = values or {}
        self.path = path
        self.root_dir = path and os.path.dirname(path)

    def reset(self, config):
        """ Reset config to the given values.

        This will completely overwrite the current configuration.
        """
        self.values = config

    def has(self, name: str) -> bool:
        return util.dict_has(self.values, name)

    def get(self, name: str, *default: Any) -> Any:
        """ Get config value with the given name and optional default.

        Args:
            name (str):
                The name of the config value.
            *default (Any):
                If given and the key doesn't not exist, this will be returned
                instead. If it's not given and the config value does not exist,
                AttributeError will be raised

        Returns:
            The requested config value. This is one of the global values defined
            in this file. If the value does not exist it will return *default* if
            give or raise `AttributeError`.

        Raises:
            AttributeError: If the value does not exist and *default* was not given.
        """
        try:
            return util.get_from_dict(self.values, f"cfg.{name}", *default)
        except KeyError:
            raise AttributeError(f"Config value '{name}' does not exist")

    def get_path(self, name: str, *default: Any) -> Any:
        """ Get config value as path relative to the project directory.

        This allows easily defining the project configuration within the fabfile
        as always relative to that fabfile.

        Args:
            name (str):
                The name of the config value containing the path.
            *default (Any):
                If given and the key doesn't not exist, this will be returned
                instead. If it's not given and the config value does not exist,
                AttributeError will be raised

        Returns:
            The requested config value. This is one of the global values defined
            in this file. If the value does not exist it will return *default* if
            give or raise `AttributeError`.

        Raises:
            AttributeError: If the value does not exist and *default* was not given.
        """
        value = self.get(name, *default)

        if value is None:
            return None

        return self.proj_path(value)

    def get_env(self, name: str, *default: Any) -> Union[str, Any]:
        """ Get the value of an ENV variable. """
        return os.environ.get(name, *default)

    def proj_path(self, *path_parts: str) -> str:
        """ Return absolute path to the repo dir (root project directory).

        Args:
            *path_parts (str):
                The path relative to the project root (pelconf.yaml).

        Returns:
            str: The given path converted to an absolute path.
        """
        parts = list(path_parts) or ['.']

        # If path represented by path_parts is absolute, do not modify it.
        if not os.path.isabs(parts[0]):

            if self.root_dir is not None:
                parts = [self.root_dir] + list(parts)

        return os.path.normpath(os.path.join(*parts))

    @contextmanager
    def within_proj_dir(self, path: str = '.') -> Iterator[None]:
        """ Return an absolute path to the given project relative path.

        :param path:
            Project relative path that will be converted to the system wide absolute
            path.
        :return:
            Absolute path.
        """
        curr_dir = os.getcwd()

        os.chdir(self.proj_path(path))
        yield
        os.chdir(curr_dir)

    @property
    def plugins(self) -> List[str]:
        return self.values.get('plugins', [])


def _load_config(path: str) -> Config:
    values = _load_from_file(path) if path else {}
    cfg = Config(values=values, path=path)

    # Prepend python_paths to sys.path. Using a clever slice notation to prepend
    # in one go.
    python_paths = [cfg.proj_path(p) for p in cfg.get('python_paths', [])]
    sys.path[0:0] = [p for p in python_paths if p not in sys.path]

    # Add scripts_dir to python paths so we can directly import all the python
    # scripts that exist there.
    scripts_dir = cfg.get_path('scripts_dir', 'scripts')
    if scripts_dir and scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    # TODO: src_dir is deprecated, use 'python_paths' config value instead.
    if cfg.has('src_dir'):
        sys.path.insert(0, cfg.get_path('src_dir'))

    for cmd in cfg.plugins:
        try:
            py_import(cmd)
        except ImportError as ex:
            log.err("Failed to load plugin <33>{}<31>: {}", cmd, ex)

    return cfg


def _load_from_file(proj_config: str):
    """ Load configuration from file. """
    if proj_config.endswith('pyproject.toml'):
        return _load_from_toml_file(proj_config)
    elif proj_config.endswith('.yaml'):
        return _load_from_yaml_file(proj_config)
    else:
        raise RuntimeError(f"Unsupported configuration {proj_config}")


def _load_from_yaml_file(path):
    """ Load config values from a YAML file. """
    with open(path) as fp:
        values = util.yaml_load(fp) or {}
        return values


def _load_from_toml_file(path):
    """ Load config values from a YAML file. """
    config = util.toml_load(path)
    values = config.get('tool', {}).get('peltak', {})
    return values


# @util.cached_result()
def _discover_proj_config() -> Optional[str]:
    """ Find the project path by going up the file tree.

    This will look in the current directory and upwards for pelconf.yaml  or
    pyproject.toml.
    """
    curr = os.getcwd()

    while curr.startswith('/') and len(curr) > 1:
        files = frozenset(os.listdir(curr))
        config_files = files & PELTAK_CONFIG_FILES
        if config_files:
            if DEFAULT_PELCONF_NAME in config_files:
                # If pelconf.yaml is present, use it. This handles both cases
                # where the project has both pelconf.yaml and pyproject.toml or
                # when it only has pelconf.yaml.
                return os.path.join(curr, DEFAULT_PELCONF_NAME)
            else:
                # If we don't have pelconf.yaml, it means we only have
                # pyproject.toml so we will use it.
                return os.path.join(curr, next(iter(config_files)))
        else:
            curr = os.path.dirname(curr)

    return None


def py_import(cmd: str) -> ModuleType:
    """ Exists only so we can patch it in tests."""
    return __import__(cmd)   # nocov
