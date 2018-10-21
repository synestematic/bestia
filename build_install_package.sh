#!/bin/bash
# https://packaging.python.org/tutorials/packaging-projects/

PACKAGE=bestia
PIP_VERSION=pip3

# build
python3 setup.py sdist bdist_wheel || exit

# install

"$PIP_VERSION" show "$PACKAGE" &>/dev/null && "$PIP_VERSION" uninstall "$PACKAGE" -y
cd dist && "$PIP_VERSION" install "$PACKAGE"-0.0.1-py3-none-any.whl
