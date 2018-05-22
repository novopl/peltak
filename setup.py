import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="fabops",
    version=read('VERSION').strip(),
    author="Mateusz 'novo' Klos",
    author_email="novopl@gmail.com",
    license="MIT",
    keywords="fabric ops devops",
    url="http://github.com/novopl/fabops",
    description="Set of fabric commands to help manage a project",
    long_description=read('README.rst'),
    package_dir={'fabops': 'src/fabops'},
    packages=find_packages('src'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
    ],
)
