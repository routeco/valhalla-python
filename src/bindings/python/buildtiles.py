from typing import List
import tarfile
from pathlib import Path
from shutil import rmtree

from .python_valhalla import _BuildTiles, _reset_actor


def BuildTiles(input_pbfs: List[str], cleanup: bool = True) -> str:
    """
    Builds and tars the routing tiles from ``input_pbfs`` according to the config.
    ``cleanup`` will remove the untarred tile files from mjolnir.tile_dir.
    Returns the path of the tar file.
    """
    from .config import _global_config

    if not input_pbfs:
        raise ValueError("No PBF files specified.")

    result = _BuildTiles(input_pbfs)
    if result is False:
        raise RuntimeError("Building tiles failed.")

    # Get the paths for the tiles
    tile_dir = Path(_global_config['mjolnir']['tile_dir'])
    tile_extract = Path(_global_config['mjolnir']['tile_extract'])
    if not tile_extract.parent.exists():
        raise ValueError("mjolnir.tile_extract={} is not inside an existing directory.".format(tile_extract.resolve()))

    tar_path = _tar_tiles(tile_dir, tile_extract, cleanup)

    _reset_actor()

    return tar_path


def _tar_tiles(tile_dir: Path, tile_extract: Path, cleanup: bool):
    """Create a TAR ball at mjolnir.tile_extract from mjolnir.tile_dir"""
    tile_dir_str = str(tile_dir.resolve())

    with tarfile.open(tile_extract, 'w') as tar:
        tar.add(tile_dir_str, arcname=tile_dir.name)

    if cleanup:
        rmtree(tile_dir_str)

    return str(tile_extract.resolve())
