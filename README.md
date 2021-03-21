# Valhalla Python

This repo only exists to build better Python bindings and package them for the most common platforms.

## Installation

### Linux

Hardest of them all.. I opted for the [`manylinux_2_24`](https://www.python.org/dev/peps/pep-0600/) which results in compatible builds for all `x86_x64` platforms (hopefully). The image is based on Debian 9, which has all dependencies packaged. Further details on compatibility are [here](https://github.com/pypa/manylinux#manylinux).

#### Pull docker image

I needed to modify the default Docker image for the `manylinux_2_24_x86_64` to keep the Python dev libraries (for `pybind11` linking):

`docker pull ghcr.io/gis-ops/manylinux_2_24_x86_64:keep_dev_libs`

#### Install dependencies

```
apt-get install -y \
  ninja-build  # v1.7.2 \
  libboost-dev-all  # v1.62 \
  libspatialite-dev  # v4.3.0a \
  libprotobuf-dev  # v3.0.0 \
  libgeos-dev  # v3.5.1 \
  libluajit-5.1-dev  # v5.1.2 \
  libcurl4-openssl-dev  # 7.52.1
```

#### Configure build

```
cd valhalla
cmake -B build_debian -G Ninja -DENABLE_TOOLS=OFF -DENABLE_SERVICES=OFF -DENABLE_TESTS=OFF -DENABLE_BENCHMARKS=OFF -DGEOS_INCLUDE_DIR=/usr/include/geos -DGEOS_LIB=/usr/lib/x86_64-linux-gnu/libgeos-3.5.1.so -DGEOS_C_LIB=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1.9.1 -DPython_LIBRARIES=/opt/python/cp36-cp36m/lib/libpython3.6m.a -DPython_INCLUDE_DIRS=/opt/python/cp36-cp36m/include/python3.6m -DPython_EXECUTABLE=/opt/python/cp36-cp36m/bin/python3.6
```

#### Build wheels

1. ``/opt/python/cp39-cp39/bin/pip wheel . -w output`

TODO: Problem is that this would produce platform-independent wheels and also not include the C++ extension. As a consequence `auditwheel` can't do its work (vendoring in valhalla's dependencies from `/usr/lib`).

Goal: make the wheel creation aware of its python version and platform, i.e. `manylinux_x86_64` or so.
