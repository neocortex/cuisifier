#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

setup(name='SuffixTree',
      version='0.1',
      ext_modules=[Extension('ukkonen', ['ukkonen.cpp'],
                             libraries=['boost_python']), ])
