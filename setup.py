import os
import re

from setuptools import find_packages, setup

with open(
    os.path.join(os.path.dirname(__file__), 'src', 'apialchemy', '__init__.py')
) as v_file:
    VERSION = (
        re.compile(r""".*__version__ = ["']([^\n]*)['"]""", re.S)
        .match(v_file.read())
        .group(1)
    )

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as r_file:
    readme = r_file.read()

setup(
    name='APIAlchemy',
    version=VERSION,
    description='API toolkit for Python, modeled after SQLAlchemy',
    long_description_content_type='text/markdown',
    long_description=readme,
    license='MIT',
    url='https://github.com/homedepot/apialchemy',
    author='Mike Phillipson',
    author_email='MICHAEL_PHILLIPSON1@homedepot.com',
    packages=find_packages('src'),
    package_dir={
        '': 'src'
    },
    install_requires=[
        'AppDynamicsRESTx',
        'PyGithub',
        'orionsdk',
        'prometheus_client',
        'prometheus-api-client',
        'splunk-sdk',
        'wavefront-sdk-python'
    ],
    zip_safe=False
)
