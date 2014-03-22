from setuptools import setup, find_packages
import json

f = open('package.json', 'r')
pkg = json.load(f)

setup(
    name='clibdoc',
    version=pkg['version'],
    description=pkg['description'],
    packages=find_packages(),
    install_requires=['jinja2'],
    data_files=[('clibdoc/data', ['data/Doxyfile.in',
                                  'data/index.html',
                                  'data/main.html',
                                  'data/clibdoc.css'])],
    scripts=['bin/clib-doc'],
)
