#!/usr/bin/env python
from __future__ import print_function

import sys

from msy import MSY

msy = MSY()
for i, p in enumerate(msy.products(sys.argv[1])):
    if i == 0:
        print("\t".join(p.keys()))
    print("\t".join(map(str, p.values())))
    
