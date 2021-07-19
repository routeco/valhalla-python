import os
import re
import sys
import time
import json
import platform
import subprocess
from pathlib import Path
from distutils import sysconfig
from sysconfig import get_paths
import multiprocessing as mp
from shutil import rmtree

try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from distutils.core import setup, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

"""
Contains partly code taken from pyosmium, partly from https://github.com/pybind/cmake_example/blob/master/setup.py
"""

BASEDIR = Path(__file__).parent
CONFIG = sysconfig.get_config_vars()
PY_MAJ = sys.version_info.major
PY_MIN = sys.version_info.minor

# Convert distutils Windows platform specifiers to CMake -A arguments
PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        super().__init__(name, sources=[])
        self.sourcedir = str(BASEDIR.resolve().absolute())


def get_python_lib(platform: str, lib_dirs):
    lib_path = None
    if platform == 'Windows':
        for d in lib_dirs:
            d = Path(d)
            if not d.exists():
                continue
            for f in d.iterdir():
                if f.name == f'python{PY_MAJ}{PY_MIN}.lib':
                    lib_path = d / f
    else:
        lib_path = Path("{}/{}".format(CONFIG['LIBDIR'], CONFIG['LDLIBRARY']))

    if not lib_path:
        raise ValueError(f"Couldn't find libpython path for platform {platform}")

    return lib_path

def get_python_include():
    return get_paths()['platinclude']


class CMakeBuild(build_ext):
    def build_extension(self, ext: Extension):
        plat = platform.system()
        extdir = str(Path(self.get_ext_fullpath(ext.name)).parent.resolve())
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep
        
        # make sure all builds happen in the same dir to be re-used
        self.build_temp = str(Path(ext.sourcedir) / "py_build")

        tmp_path = Path(self.build_temp)
        if not tmp_path.exists():
            tmp_path.mkdir(parents=True)

        if Path(tmp_path / 'CMakeFiles').exists():
            rmtree(str(tmp_path / 'CMakeFiles'))
        if Path(tmp_path / 'CMakeCache.txt').exists():
            os.remove(str(tmp_path / 'CMakeCache.txt'))
        
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        cfg = 'Debug' if self.debug else 'Release'

        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(extdir),
                      '-DPython_EXECUTABLE={}'.format(sys.executable),
                      '-DPython_INCLUDE_DIRS={}'.format(get_python_include()),
                      '-DPython_LIBRARIES={}'.format(get_python_lib(plat, self.library_dirs)),
                      '-DCMAKE_BUILD_TYPE={}'.format(cfg),
                      '-DENABLE_BENCHMARKS=OFF',
                      '-DENABLE_TESTS=OFF',
                      '-DENABLE_TOOLS=OFF',
                      '-DENABLE_SERVICES=OFF',
                      '-DENABLE_CCACHE=OFF',
                      '-DENABLE_BENCHMARKS=OFF']
        build_args = []

        cpu_count = mp.cpu_count() if mp.cpu_count() < 4 else mp.cpu_count() - 1

        if self.compiler.compiler_type != "msvc":
            cmake_args += ["-GNinja"]
            build_args += ['--', "-j{}".format(cpu_count)]
        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            if not single_config:
                cmake_args += [
                    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), extdir)
                ]
                build_args += ["--config", cfg]
                build_args += ["--", f"/maxcpucount:{str(cpu_count)}"]

        env = os.environ.copy()

        if env.get('VCPKG_TARGET_TRIPLET'):
            cmake_args += ['-DVCPKG_TARGET_TRIPLET={}'.format(env['VCPKG_TARGET_TRIPLET'])]
        if env.get('CMAKE_TOOLCHAIN_FILE'):
            cmake_args += ['-DCMAKE_TOOLCHAIN_FILE={}'.format(env['CMAKE_TOOLCHAIN_FILE'])]
        if env.get('LUA_INCLUDE_DIR'):
            cmake_args += ['-DLUA_INCLUDE_DIR={}'.format(env['LUA_INCLUDE_DIR'])]
        if env.get('LUA_LIBRARIES'):
            cmake_args += ['-DLUA_LIBRARIES={}'.format(env['LUA_LIBRARIES'])]

        subprocess.check_call(['cmake', '-S{}'.format(ext.sourcedir)] + cmake_args, cwd=str(tmp_path), env=env)
        
        # we need to remove all previously generated shared libraries from the build folder!
        so_path = tmp_path.joinpath("src", "bindings", "python", "valhalla")
        
        for f in so_path.iterdir():
            if f.suffix in ('.so', '.dylib', '.dll') and 'python_valhalla' in f.name:
                print(f"\nRemoving shared lib: {f.name}\n")
                f.unlink()

        subprocess.check_call(['cmake', '--build', str(tmp_path.resolve().absolute())] + build_args)

if sys.version_info < (3, 7):
    raise RuntimeError("Python 3.7 or larger required.")

# Before all else remove the lib.<platform> dir to get rid of previous build shared lib
lib_path = BASEDIR / 'build'
for d in lib_path.iterdir():
    if 'lib.' in str(d.resolve()):
        rmtree(str(d))
        print(f"\nRemoved the lib dir {d}\n")

# it's pretty confusing: on first cmake build this will fail the build, since it can't
# find a package in the new build folder (checks very first to copy everything from the
# build folder!!). After the first build there will be package in the build dir, so the 
# second build can copy the files as first action. The subsequent build is bullocks 
# actually. Maybe I'm just using it wrong.. 
#
# Long story short: ALWAYS build the bindings TWICE for each python version.
setup(
    name="valhalla",
    version=time.strftime("%d-%m-%Y"),
    ext_modules=[CMakeExtension('valhalla')],
    package_dir={'': str(Path('py_build/src/bindings/python'))},
    packages=find_packages(where=str(Path(f'py_build/src/bindings/python').resolve().absolute())),
    package_data={'valhalla': ['*.dll', '*.so', '*.dylib']},
    python_requires=">=3.6",
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
