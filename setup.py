#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import site

from distutils.command.build_scripts import build_scripts
from distutils import util, log

try:
    from setuptools import setup, Extension
    args = {
        'test_suite': 'test',
        'zip_safe': False,
    }
except ImportError:
    from distutils.core import setup, Extension
    args = {}

from Cython.Distutils import build_ext


class build_scripts_rename(build_scripts):
    def copy_scripts(self):
        build_scripts.copy_scripts(self)
        # remove the .py extension from scripts
        for s in self.scripts:
            f = util.convert_path(s)
            before = os.path.join(self.build_dir, os.path.basename(f))
            after = os.path.splitext(before)[0]
            log.info("renaming %s -> %s" % (before, after))
            os.rename(before, after)


cmdclass = {
    'build_scripts': build_scripts_rename,
    'build_ext': build_ext,
}

usp = site.getusersitepackages()
rel_usp = os.path.relpath(usp, start=site.USER_BASE)

# DLL compiled w/ Visual Studio 2019.
# Didn't seem to work, maybe b/c something w/ drive prefix.
# Relative path from setup.py to DLL also seemed not to work, but maybe for same
# reason, and not cause it couldn't.
#dll_path = 'C:/Users/tom/src/liblo/cmake/out/install/x64-Debug/bin/liblo.dll'
dll_path = 'C:\\Users\\tom\\src\\liblo\\cmake\\out\\install\\x64-Debug\\bin\\liblo.dll'
assert os.path.isfile(dll_path)
dll_dir = os.path.dirname(dll_path)
assert os.path.isdir(dll_dir)

renamed_dll_path = os.path.join(os.path.dirname(dll_path), 'lo.dll')
assert os.path.isfile(renamed_dll_path)

ext_modules = [
    Extension(
        'liblo',
        ['src/liblo.pyx'],
        extra_compile_args = [
            # none of these are recognized by windows compiler and last two
            # activly cause compilation to fail
            #'-fno-strict-aliasing',
            #'-Werror-implicit-function-declaration',
            #'-Wfatal-errors',
        ],

        # TODO TODO do i need to point to any windows specific library dirs here
        # or below for compilation outputs to actually work? some SO post (i
        # forget exactly which) seemed to suggest that one of these normally has
        # windows stuff referenced...

        # TFO: Changed 'lo' to 'liblo' under 'libraries' key.
        # TODO how does it translate this name into the names of files to look
        # for? does it? can i just rename them if so, or is something baked into
        # the build artifacts that would prevent that from working?

        # (this wouldn't work unless i copied liblo.lib to lo.lib in the same
        # folder)
        libraries = ['lo'],
        # (this let compilation work w/o having to rename the .lib file, but it
        # may or may not have been part of the reason things ultimately failed
        # later)
        #libraries = ['liblo'],

        # TFO: Added the following options pointing to my outputs of Visual
        # Studio liblo compilation.
        library_dirs=['C:/Users/tom/src/liblo/cmake/out/install/x64-Debug/lib'],
        # TODO does this ever work on windows? yielding warning that this is
        # unused w/ pip.exe install ./pyliblo/ --user -vvv
        #runtime_library_dirs=[dll_dir],
        # TODO could try adding dll path to runtime_library_dirs?
        # (though not sure if that ultimately does something different than what
        # i do w/ data_dirs below...)
        include_dirs=[
            'C:/Users/tom/src/liblo/cmake/out/install/x64-Debug/include'
        ],
    )
]


setup(
    name = 'pyliblo',
    version = '0.10.0',
    author = 'Dominic Sacré',
    author_email = 'dominic.sacre@gmx.de',
    url = 'http://das.nasophon.de/pyliblo/',
    description = 'Python bindings for the liblo OSC library',
    license = 'LGPL',
    scripts = [
        'scripts/send_osc.py',
        'scripts/dump_osc.py',
    ],
    data_files = [
        ('share/man/man1', [
            'scripts/send_osc.1',
            'scripts/dump_osc.1',
        ]),
        # TFO: added this
        (rel_usp, [dll_path]),
        # maybe this will work?
        (rel_usp, [renamed_dll_path])
    ],
    cmdclass = cmdclass,
    ext_modules = ext_modules,
    **args
)
