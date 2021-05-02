## Installation

### Linux

Hardest of them all.. I opted for the [`manylinux_2_24`](https://www.python.org/dev/peps/pep-0600/) which results in compatible builds for all `x86_x64` platforms (hopefully). The image is based on Debian 9, which has all dependencies packaged. Further details on compatibility are [here](https://github.com/pypa/manylinux#manylinux).

#### Pull docker image

I needed to modify the default Docker image for the `manylinux_2_24_x86_64` to keep the Python dev libraries (for `pybind11` linking):

`docker pull ghcr.io/gis-ops/manylinux_2_24_x86_64:keep_dev_libs`

#### Install dependencies

**In the above image those deps are already pre-installed.**

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

We only need to configure the build to produce the `setup.py`

```
cd valhalla
cmake -B build -G Ninja -DENABLE_TOOLS=OFF -DENABLE_SERVICES=OFF -DENABLE_TESTS=OFF -DENABLE_BENCHMARKS=OFF -DGEOS_INCLUDE_DIR=/usr/include/geos -DGEOS_LIB=/usr/lib/x86_64-linux-gnu/libgeos-3.5.1.so -DGEOS_C_LIB=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1.9.1 -DPython_LIBRARIES=/opt/python/cp36-cp36m/lib/libpython3.6m.a -DPython_INCLUDE_DIRS=/opt/python/cp36-cp36m/include/python3.6m -DPython_EXECUTABLE=/opt/python/cp36-cp36m/bin/python3.6
```

#### Build wheels

The `setup.py` will be available after a CMake step in the project root.

1. Builds the project to `./build` and installs to `./dist` (**RUN TWICE** for some reason): `/opt/python/cp36-cp36m/bin/python3.6 setup.py bdist_wheel` and a wheel to `dist`
2. For Linux, repair the wheel (copies missing libraries and renames the wheel): `auditwheel repair dist/valhalla-3.1.0-cp36-cp36m-linux_x86_64.whl --plat manylinux_2_24_x86_64`
3. Find the wheel(s) in `./dist/wheelhouse`.

Gotchas:
- easiest with `setup.py` in the root directory!
- shared Python lib wasn't copied into the wheel, had to do setup.py's `package_data` trick

### Windows

#### Build wheels

**Python3.6 does not work**, some error in mjolnir/util.h.. Can't understand why, Python version shouldn't at all have an influence here..

With MSVC:

```
call .windows_env.bat & C:\Users\nilsn\AppData\Local\Programs\Python\Python39\python.exe setup.py bdist_wheel
```

Building multiple subsequent Python versions with MSVC (not Ninja) works well: 1-2 mins per build. I'd recommend starting with 3.7 and working our way up.

#### Troubleshooting

1. If it complains about CURL, then likely CMake chose the wrong architecture (x86): check which CXX compiler was used in the CMake configure step. Mostly a problem in VS Code's auto cmake step. Solution: use the VS 2019 dev cmd prompt with manual commands:

```
"C:\Program Files\CMake\bin\cmake.EXE" --no-warn-unused-cli -DENABLE_TOOLS:STRING=OFF -DENABLE_HTTP:STRING=OFF -DENABLE_DATA_TOOLS:STRING=ON -DENABLE_PYTHON_BINDINGS:STRING=ON -DENABLE_SERVICES:STRING=OFF -DENABLE_TESTS:STRING=OFF -DENABLE_CCACHE:STRING=OFF -DENABLE_COVERAGE:STRING=OFF -DENABLE_BENCHMARKS:STRING=OFF -DLUA_INCLUDE_DIR:STRING=C:\Users\nilsn\Documents\dev\vcpkg\installed\x64-windows\include\luajit -DLUA_LIBRARIES:STRING=C:\Users\nilsn\Documents\dev\vcpkg\installed\x64-windows\lib\lua51.lib -DPython_EXECUTABLE:STRING=C:\Users\nilsn\AppData\Local\Programs\Python\Python39 -DPython_LIBRARIES:STRING=C:\Users\nilsn\AppData\Local\Programs\Python\Python39\libs\python39.lib -DPython_INCLUDE_DIRS:STRING=C:\Users\nilsn\AppData\Local\Programs\Python\Python39\include -DCMAKE_TOOLCHAIN_FILE:STRING=C:\Users\nilsn\Documents\dev\vcpkg\scripts\buildsystems\vcpkg.cmake -DVCPKG_TARGET_TRIPLET:STRING=x64-windows -DCMAKE_BUILD_TYPE:STRING=Release -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -Hc:/Users/nilsn/Documents/dev/cpp/valhalla-python -Bc:/Users/nilsn/Documents/dev/cpp/valhalla-python/build -G "Visual Studio 16 2019" -T host=x64 -A win64
```
