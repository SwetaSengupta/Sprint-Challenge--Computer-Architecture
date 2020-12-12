#!/usr/bin/env python3

"""Main."""
import sys
from cpu import CPU

# CPU file and file we are running
if len(sys.argv) == 2:
    cpu_new = CPU()

    cpu_new.load()
    cpu_new.run()
else:
    print('Error: Need file name')
    sys.exit(1)