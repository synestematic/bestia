#!/bin/bash
# https://packaging.python.org/tutorials/packaging-projects/

PACKAGE=bestia
PACKAGE_VERSION=0.1.0 # set according to setup.py 
PIP_VERSION=pip3
PURGE_DIRS=(dist build "$PACKAGE".egg-info)

# build
python3 setup.py sdist bdist_wheel || exit

# install
"$PIP_VERSION" show "$PACKAGE" &>/dev/null && "$PIP_VERSION" uninstall "$PACKAGE" -y
cd dist && "$PIP_VERSION" install "$PACKAGE"-"$PACKAGE_VERSION"-py3-none-any.whl && cd ..

# clean-up
for dir in "${PURGE_DIRS[@]}"; do
    [ -d "$dir" ] && rm -rf "$dir" && echo "deleted $dir directory"
done

# upload
# twine upload --repository-url https://test.pypi.org/legacy/ dist/*


