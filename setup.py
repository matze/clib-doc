from setuptools import setup, find_packages
import json

def read_from_package():
    with open('package.json', 'r') as f:
        pkg = json.load(f)
        return dict(version=pkg['version'],
                    description=pkg['description'])

setup(
    name='clibdoc',
    packages=find_packages(),
    install_requires=['jinja2'],
    data_files=[('clibdoc/data', ['data/Doxyfile.in',
                                  'data/index.html',
                                  'data/main.html',
                                  'data/clibdoc.css'])],
    scripts=['bin/clib-doc'],
    **read_from_package()
)
