import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bestia",
    version="0.8.6",
    author="Federico Rizzo",
    author_email="foo@bar.com",
    description="A collection of tools for building dynamic Command-Line applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/synestematic/bestia",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
    ],
    install_requires=[
        'pyperclip',
        'python-magic',
        'requests',
        'termcolor',
    ],
)
