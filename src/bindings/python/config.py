import json
import os

_global_config = dict()


def get_default() -> dict:
    """Returns the default Valhalla configuration."""
    from .valhalla_build_config import config as _config, optional as _optional
    c = _config.copy()
    for k, v in c['mjolnir'].items():
        if isinstance(v, _optional):
            c['mjolnir'][k] = ""
    return c


def get_help() -> dict:
    from .valhalla_build_config import help_text as _help_text
    """Returns the help texts to the Valhalla configuration."""
    return _help_text


def _create_config(path: str, c: dict, tile_dir: str, tile_extract: str, verbose: bool) -> bool:
    # set a global config so that other modules can work with it
    global _global_config
    conf = c.copy()

    # Configuring for the first time
    changed = False if _global_config else True

    if os.path.exists(path) and not conf:
        # use the existing file if one exists and no config was passed
        with open(path) as f:
            conf = json.load(f)
    elif not conf:
        # if the file doesn't exist and no config was passed, raise
        raise ValueError("No local config file found, you need to specify a configuration to create one.")
    
    # Write the convenience stuff
    conf["loki"]["logging"]["type"] = "std_out" if verbose is True else ""
    if tile_dir:
        conf["mjolnir"]["tile_dir"] = tile_dir
    if tile_extract:
        conf["mjolnir"]["tile_extract"] = tile_extract
        changed = True

    # Finally write the config to filesystem
    with open(path, 'w') as f:
        json.dump(conf, f, indent=2)

    _global_config = conf

    return changed
