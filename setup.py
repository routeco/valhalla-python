import os
import re
import shutil
import sys
import time
import json
import platform
import subprocess
from distutils.command.install_data import install_data
from pathlib import Path
from distutils import sysconfig
from sysconfig import get_paths
import multiprocessing as mp
from shutil import rmtree

from setuptools.command.install_lib import install_lib

try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from distutils.core import setup, find_packages
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

"""
Contains partly code taken from pyosmium, partly from https://github.com/pybind/cmake_example/blob/master/setup.py
Big help as well: https://stackoverflow.com/a/51575996/2582935
"""

PACKAGENAME = "valhalla"
BASEDIR = Path(__file__).parent.resolve()
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


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class InstallCMakeLibsData(install_data):
    """
    Just a wrapper to get the install data into the egg-info

    Listing the installed files in the egg-info guarantees that
    all of the package files will be uninstalled when the user
    uninstalls your package through pip
    """
    def run(self):
        """
        Outfiles are the libraries that were built using cmake
        """
        self.outfiles = self.distribution.data_files


class InstallCMakeLibs(install_lib):
    """
    Get the libraries from the parent distribution, use those as the outfiles

    Skip building anything; everything is already built, forward libraries to
    the installation step
    """

    def run(self):
        """
        Copy libraries from the bin directory and place them as appropriate
        """
        self.skip_build = True
        bin_dir = Path(self.distribution.bin_dir)

        libs = filter(lambda p: p.is_file() and p.suffix in [".dll", ".so", ".dylib"] and not ("python" in p.name or PACKAGENAME in p.name), bin_dir.iterdir())
        for lib in libs:
            shutil.move(str(lib), self.build_dir)

        self.distribution.data_files = [str(lib)
                                        for lib in libs]

        # Must be forced to run after adding the libs to data_files
        self.distribution.run_command("install_data")

        super().run()


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        super().run()

    def build_extension(self, ext: Extension):
        build_dir = Path("build_py").resolve()  # the root of ./build/temp_xxx dir
        self.build_temp = str(build_dir)
        ext_dir = Path(self.get_ext_fullpath(ext.name)).parent.resolve()  # where setuptools collects the built files before building the wheel 
        lib_dir = ext_dir.joinpath(PACKAGENAME).resolve()  # the above + ./valhalla
        bin_dir = build_dir.joinpath('src', 'bindings', 'python', 'valhalla').resolve()  # where the py sources are (and UNIX .so/.dylib)
        
        #if not ext_dir.endswith(os.path.sep):
        #    ext_dir += os.path.sep

        build_dir.mkdir(parents=True, exist_ok=True)
        lib_dir.mkdir(parents=True, exist_ok=True)  # also creates ext_dir

        plat = platform.system()
        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")
        cfg = 'Debug' if self.debug else 'Release'

        cmake_args = ['-DPython_EXECUTABLE={}'.format(sys.executable),
                      '-DPython_INCLUDE_DIRS={}'.format(get_python_include()),
                      '-DPython_LIBRARIES={}'.format(get_python_lib(plat, self.library_dirs)),
                      '-DENABLE_BENCHMARKS=OFF',
                      '-DENABLE_TESTS=OFF',
                      '-DENABLE_DATA_TOOLS=OFF',
                      '-DENABLE_TOOLS=OFF',
                      '-DENABLE_SERVICES=OFF',
                      '-DENABLE_CCACHE=OFF',
                      '-DENABLE_BENCHMARKS=OFF']
        build_args = []

        cpu_count = mp.cpu_count() if mp.cpu_count() < 4 else mp.cpu_count() - 1

        if plat != "Windows":
            cmake_args += ["-GNinja"]
            build_args += ['--', "-j{}".format(cpu_count)]
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
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
                    "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), lib_dir)
                ]
                build_args += ["--config", cfg]
                build_args += ["--", f"/maxcpucount:{str(cpu_count)}"]

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(env.get('CXXFLAGS', ''),
                                                              self.distribution.get_version())

        if env.get('VCPKG_TARGET_TRIPLET'):
            cmake_args += ['-DVCPKG_TARGET_TRIPLET={}'.format(env['VCPKG_TARGET_TRIPLET'])]
        if env.get('CMAKE_TOOLCHAIN_FILE'):
            cmake_args += ['-DCMAKE_TOOLCHAIN_FILE={}'.format(env['CMAKE_TOOLCHAIN_FILE'])]
        if env.get('LUA_INCLUDE_DIR'):
            cmake_args += ['-DLUA_INCLUDE_DIR={}'.format(env['LUA_INCLUDE_DIR'])]
        if env.get('LUA_LIBRARIES'):
            cmake_args += ['-DLUA_LIBRARIES={}'.format(env['LUA_LIBRARIES'])]
                
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
        
        self.distribution.bin_dir = str(bin_dir)  # no idea what that does..

        # collect the built files..
        if plat == 'Windows':
            # for windows we need to copy the .dlls from another directory, build/Release
            lib_paths = filter(lambda p: p.is_file() and p.suffix in [".py", ".pyd", ".dll"], list(bin_dir.iterdir()) + list(build_dir.iterdir()))
        else:
            lib_paths = filter(lambda p: p.is_file() and p.suffix in [".py", ".pyd", ".so", ".dylib"], bin_dir.iterdir())

        # manually copy over the built files..
        for p in lib_paths:
            p = p.resolve()
            d = lib_dir.joinpath(p.name)
            if d.exists():
                d.unlink()
            shutil.move(str(p), str(d))
            print(f"copying {p.relative_to(BASEDIR)} -> {lib_dir.relative_to(BASEDIR)}")


if sys.version_info < (3, 7):
    raise RuntimeError("Python 3.7 or larger required.")


setup(
    name="valhalla",
    version=time.strftime("%Y.%m.%d"),
    ext_modules=[CMakeExtension('valhalla')],
    packages=find_packages(),
    python_requires=">=3.7",
    cmdclass=dict(
        build_ext=CMakeBuild,
        install_data=InstallCMakeLibsData,
        install_lib=InstallCMakeLibs
    ),
    zip_safe=False,
)
