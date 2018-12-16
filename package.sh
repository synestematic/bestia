#!/bin/bash
# https://packaging.python.org/tutorials/packaging-projects/

echo_green() { echo -e "\033[01;32m$1\033[00m"; }
echo_magenta() { echo -e "\033[01;35m$1\033[00m"; }

PACKAGE=bestia
PACKAGE_VERSION=`cat setup.py | awk -F"\"|\'" '/version/{print $2}'`
PURGE_DIRS=(dist build "$PACKAGE".egg-info)

# build
echo_magenta "Building $PACKAGE $PACKAGE_VERSION..."
python3 setup.py sdist bdist_wheel && echo_green "Success" || exit

# install
pip3 show "$PACKAGE" &>/dev/null && (echo_magenta "Uninstalling old version"; pip3 uninstall "$PACKAGE" -y )
echo_magenta "Installing $PACKAGE $PACKAGE_VERSION"
cd dist && pip3 install "$PACKAGE"-"$PACKAGE_VERSION"-py3-none-any.whl && cd ..

# upload to PyPI
[ "$1" == '--upload' ] && (echo_magenta "Uploading to PyPI "; twine upload dist/*)

# clean up
echo_magenta "Cleaning up"
for dir in "${PURGE_DIRS[@]}"; do
    [ -d "$dir" ] && rm -rf "$dir" && echo "Deleted $dir directory"
done
