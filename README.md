## clib-doc

Generate documentation from a clib module or a whole directory of modules.


### Installation

Install `clib-doc` either via

    $ python setup.py install

or through `clib`

    $ clib install matze/clib-doc

You also need Doxygen which is used to parse the sources. On Debian systems run

    $ apt-get install doxygen


### Usage

You can generate API documentation for a single module by passing the path to
a `package.json` file

    $ clib-doc --package ~/foo/bar/package.json

or run it inside a directory with a pre-populated `deps/` sub-directory:

    $ clib-doc
    $ xdg-open _docs/index.html


### License

clib-doc is licensed under the MIT license.
