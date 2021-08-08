import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="bestia",
    version="4.0",
    author="Federico Rizzo",
    author_email="synestem@ticATgmail.com",
    description="A collection of tools for building dynamic Command-Line applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synestematic/bestia",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    install_requires=[],
)
