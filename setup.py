import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bestia",
    version="0.1.0",
    author="Federico Rizzo",
    author_email="yo@gmail.com",
    description="A collection of tools for building dynamic Command-Line applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synestematic/bestia",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
