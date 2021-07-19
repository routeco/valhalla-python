#!/usr/bin/env bash

set -eu

function usage() {
	echo "Usage: valhalla_path python_minor_version cleanup_bool, e.g. ./build_linux_py_libs.sh $PWD 9 false"
	exit 1
}

function find_files() {
   find ${1}/ -type f -printf "%f\n"
}

valhalla_src=$1
py_min=$2
cleanup=$3

py_allowed="7 8 9"
if [[ ! ${py_allowed} == *"${py_allowed}"* ]]; then
  echo "${py_min} is not a supported Python minor version. Choose one of ${py_allowed}"
  usage
fi

# first clean up a little
pip uninstall -y valhalla

if [[ $cleanup == "true" ]]; then
  if  [[ ! -z $(find_files ${valhalla_src}/wheelhouse) ]]; then
    rm ${valhalla_src}/wheelhouse/*
  fi
  if  [[ ! -z $(find_files ${valhalla_src}/dist) ]]; then
    rm ${valhalla_src}/dist/*
  fi
fi

# determine the python version and the directory to use
case ${py_min} in
  7)
    py_dir=cp37-cp37m
    ;;
  8)
    py_dir=cp38-cp38
    ;;
  9)
    py_dir=cp39-cp39
    ;;
esac

# run manylinux container
container=$(docker run -dt --name python-valhalla-linux -v ${valhalla_src}:/valhalla registry.gitlab.com/gis-ops/manylinux:incl_dev_libs)

# remember: build twice
docker exec ${container} /bin/bash -c "cd /valhalla && /opt/python/${py_dir}/bin/python3.${py_min} setup.py bdist_wheel"
docker exec ${container} /bin/bash -c "cd /valhalla && /opt/python/${py_dir}/bin/python3.${py_min} setup.py bdist_wheel"

# repair the wheel for manylinux tag
wheel=$(find_files dist)
docker exec ${container} /bin/bash -c "cd /valhalla && auditwheel repair dist/${wheel} --plat manylinux_2_24_x86_64"
audit_wheel=$(find ${valhalla_src}/wheelhouse/ -type f -printf "%f\n")

docker rm -f ${container}

pip install --no-input ${valhalla_src}/wheelhouse/${audit_wheel}
