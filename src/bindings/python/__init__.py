try:
    from .python_valhalla import Configure
except ModuleNotFoundError:
    from python_valhalla import Configure
from ._actions import *
from .buildtiles import BuildTiles
