#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced interface to install/remove or search for packages.

See `adapt install -h` or `adapt search -h` for more information.
"""

import sys
import adapt.install
import adapt.search

modules = {"install": adapt.install,
           "search": adapt.search}

arg0, *args = sys.argv[1:]

if arg0 in ["-h" or "--help"]:
    print(__doc__.strip())
elif (mod:=modules.get(arg0, None)) is not None:
    mod.main(*args)
else:
    print(f"Unknown option '{arg0}'. Please see 'adapt -h' for usage")
