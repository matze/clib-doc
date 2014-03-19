from setuptools import setup, find_packages

setup(
    name='clibdoc',
    version='0.1.0',
    packages=find_packages(),
    data_files=[('clibdoc/data', ['data/Doxyfile.in',
                                  'data/index.html',
                                  'data/clibdoc.css'])],
    scripts=['bin/clib-doc']
)
