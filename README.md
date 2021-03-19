# Valhalla Python

This repo only exists to build better Python bindings and package them for the most common platforms.

## Installation

### Linux

Hardest of them all.. I opted for the [`manylinux2014`](https://www.python.org/dev/peps/pep-0599/) which results in compatible builds for all `x86_x64` platforms (hopefully). The image is based on CentOS 7, which has all dependencies packaged. Further details on compatibility are [here](https://github.com/pypa/manylinux#manylinux).

#### Dependencies

- `boost-devel.x86_64` v1.53
- `sqlite-devel.x86_64` v3.7.17
- `libspatialite-devel.x86_64` v4.1.1
- `protobuf-devel.x86_64` v2.5.0
- `libcurl-devel.x86_64` v7.29.0
- `luajit-devel.x86_64` v2.0.4
- `python3-devel.x86_64` v3.6.8
- `geos-devel.x86_64` 3.4.2
