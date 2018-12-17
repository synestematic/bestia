PACKAGE = bestia
PACKAGE_VERSION = 0.8.6
PURGE_DIRS = dist build ${PACKAGE}.egg-info

default: build install clean

upload: build install publish clean

build: setup.py ${PACKAGE}
	@echo "Building ${PACKAGE} ${PACKAGE_VERSION}..."
	@python3 setup.py sdist bdist_wheel && echo "Success" || exit

install: ${PURGE_DIRS}
	@pip3 show "${PACKAGE}" &>/dev/null && (echo "Uninstalling old version"; pip3 uninstall "${PACKAGE}" -y )
	@echo "Installing ${PACKAGE} ${PACKAGE_VERSION}"
	@cd dist && pip3 install "${PACKAGE}"-"${PACKAGE_VERSION}"-py3-none-any.whl && cd ..

publish: dist
	@echo "Uploading to PyPI "
	@twine upload dist/*

clean: ${PURGE_DIRS}
	@echo "Cleaning up"
	@for dir in ${PURGE_DIRS} ; do \
		[ -d "$${dir}" ] && rm -rf "$${dir}" && echo "Deleted $${dir} directory" \ ; \
	done
