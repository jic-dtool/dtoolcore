from setuptools import setup


version = "3.10.0"
url = "https://github.com/jic-dtool/dtoolcore"
readme = open('README.rst').read()

setup(
    name="dtoolcore",
    packages=["dtoolcore"],
    version=version,
    description="Core API for managing (scientific) data",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    download_url="{}/tarball/{}".format(url, version),
    install_requires=[],
    entry_points={
        "dtool.storage_brokers": [
            "DiskStorageBroker=dtoolcore.storagebroker:DiskStorageBroker",
        ],
    },
    license="MIT"
)
