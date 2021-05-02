import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from .python_valhalla import _reset_actor

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


def _create_config(path: str, tile_extract: str, c: dict, verbose: bool):
    # set a global config so that other modules can work with it
    global _global_config
    conf = c.copy()

    if os.path.exists(path) and not conf:
        # use the existing file if one exists and no config was passed
        with open(path) as f:
            conf = json.load(f)
    elif not conf:
        # if the file doesn't exist, create it and get the default config
        conf = get_default()
        os.makedirs(os.path.dirname(path), exist_ok=True)

    # Check if the tile_dir exists and create a temp dir if not
    tile_dir = conf['mjolnir']['tile_dir']
    if not tile_dir or not Path(tile_dir).exists():
        temp_dir = TemporaryDirectory()  # needs to be created explicitly
        tile_dir = Path(temp_dir.name)
    tile_dir = Path(tile_dir)
    if not tile_dir.is_dir():
        raise ValueError("mjolnir.tile_dir={} is not a directory".format(tile_dir.resolve()))
    conf['mjolnir']['tile_dir'] = str(tile_dir.resolve())
    
    # Write the convenience stuff
    conf["loki"]["logging"]["type"] = "std_out" if verbose is True else ""
    # If the tile extract path does not exist, raise
    if not tile_extract:
        tile_extract = 'valhalla_tiles.tar'
    conf["mjolnir"]["tile_extract"] = str(Path(tile_extract).resolve())

    # Finally write the config to the filesystem
    with open(path, 'w') as f:
        json.dump(conf, f, indent=2)

    _global_config = conf

    return
