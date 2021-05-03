# Valhalla for Python

This spin-off project simply offers improved Python bindings to the fantastic [Valhalla project](https://github.com/valhalla/valhalla). 

The improvements to Valhalla's native bindings are:

- build routing tiles from Python API
- easier configuration of Valhalla
- re-configure the routing engine with different parameters (e.g. maximum limits) or change routing tiles
- some utilities: decoding polylines (more planned)

> Disclaimer: This is a third-party clone of Valhalla where (almost) only Python related code was changed. We regularly merge the Valhalla core to stay up-to-date.

## Planned Features

- [ ] Download tile packs for Valhalla
- [ ] Download admin & timezone DBs

## Installation
 
`pip install valhalla`

We package CPython 3.7, 3.8, 3.9 **wheels** for Win64, ~~MacOS X~~ (soon) and Linux distributions with `glibc>=2.24` (most modern systems, see [PEP 600](https://www.python.org/dev/peps/pep-0600/)). We **do not** offer a source distribution on PyPI. Please contact us on enquiry@gis-ops.com if you need support building the bindings for your platform.

## Usage

Typically you'd take these steps:

### 1. Configure Valhalla

Valhalla expects a config JSON to know where to put the routing tiles, applying service limits etc. If you don't have an existing Valhalla JSON, one will be created for you at the specified path. If you don't specify your own `config` dictionary and the config JSON doesn't exist, the default will apply from `valhalla.config.get_default()`. If the config JSON does exist and `config` is specified, the config file will be overwritten.

**Note**, if you want to change parameters or the routing tiles, you'll need to call `Configure()` again with the new parameters.

```python
from valhalla import Configure, config

# Will create valhalla.json with the default configuration
Configure('./valhalla.json', './valhalla_tiles.tar', verbose=True)
# or pass a configuration explicitly: good for changing defaults
conf = config.get_default()
conf['mjolnir']['tile_dir'] = './'
conf['mjolnir']['service_limits']['bicycle']['max_locations'] = 500
Configure('./valhalla.json', './valhalla_tiles.tar', conf)
```

### 2. Build Tiles

If `./valhalla_tiles.tar` is not an existing tile pack, you'll have to build the routing tiles first. Download one or multiple OSM PBF files (e.g. from [Geofabrik](https://download.geofabrik.de)) and pass a list of the file paths to `valhalla.BuildTiles()`. This will create tile files at `mjolnir.tile_dir` path from the configuation (default a temporary path) and tar up all tiles to the file path at `mjolnir.tile_extract`. If `cleanup` is `True` (default) the tile files will be deleted automatically.

**Note**, Windows users won't be able to use admin or timezone DBs currently due to a [bug in Valhalla](https://github.com/valhalla/valhalla/issues/3010).

```python
from valhalla import BuildTiles

# Will print the log to stdout if Configure() was called with verbose=True
BuildTiles(['./andorra-latest.osm.pbf'])
tar_pat = Path('./valhalla_tiles.tar')
assert tar_path.exists()
assert tar_path.stat().st_size > 10000  # file size > 10 kB
```

### 3. Execute action (Route/Isochrone/Matrix etc.)

After you configured the service and if there are routable tiles you can call any of the Valhalla actions (see `loki.actions` for a list). The actions support the same format as a Valhalla HTTP API request, either as `dict` or as `str`.

Valhalla encodes the geometry for a routing request with [Google's polyline algorithm](https://developers.google.com/maps/documentation/utilities/polylinealgorithm) and a precision of 6. For convenience, we included a polyline decoder in `valhalla.utils.decode_polyline()`.

```python
import json
from valhalla import Route, utils

query = {"locations": [{"lat": 42.560225, "lon": 1.575251}, {"lat": 42.553396, "lon": 1.541176}], "costing": "auto", "directions_options": {"language": "ru-RU"}}
route = Route(query)

json.dumps(route, indent=2)

# Get the geometry as coordinate array, default in [lng, lat] order
coords = utils.decode_polyline(route['trip']['legs'][0]['shape'], order='latlng')
print(coords)
```

## Known limitations

- Windows users won't be able to build tiles with support for admin & timezone DBs (see https://github.com/valhalla/valhalla/issues/3010)

## Release pattern

Releases of the Python wheels on PyPI will have the pattern `<bindings_version>-<YYYY-MM-DD>`, where the date information is relating to the merge date of Valhalla core (approx. midnight CE(S)T). We're planning to merge Valhalla core code once a month, unless there's critical bug fixes.
