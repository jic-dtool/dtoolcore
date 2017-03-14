from setuptools import setup

url = ""
version = "0.13.0"
readme = open('README.rst').read()

setup(name="dtoolcore",
      packages=["dtoolcore"],
      version=version,
      description="Core API for managing (scientific) data",
      long_description=readme,
      include_package_data=True,
      author="Tjelvar Olsson",
      author_email="tjelvar.olsson@jic.ac.uk",
      url=url,
      install_requires=[
        "pyyaml",
        "python-magic",
      ],
      download_url="{}/tarball/{}".format(url, version),
      license="MIT")
