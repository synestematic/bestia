# https://packaging.python.org/tutorials/packaging-projects/

#######################################
# to build your distro run:
#    python3 setup.py sdist bdist_wheel
#
# dist/
#   bestia-0.0.1-py3-none-any.whl
#   bestia-0.0.1.tar.gz

#######################################
# to install your distro run:
#    pip3 install bestia-0.0.1-py3-none-any.whl

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bestia",
    version="0.0.1",
    author="Federico Rizzo",
    author_email="yo@gmail.com",
    description="Tools for interacting with web services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synestematic/bestia",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
