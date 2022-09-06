"""
Simple python script to fix the wrong path in the json files.

Example:

{"IDBs/Dataset-1/z3/x64-gcc-4.8-O0_z3.i64": [ ... ], ... }

would become

{"IDBs/Dataset-1/x64-gcc-4.8-O0_z3.i64": [ ... ], ... }
"""

import sys, json


def usage():
    print('Usage: python fix-json.py FILENAME')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        exit(1)
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
    jData = {'/'.join((l:=k.split('/'))[:2]+l[3:]): v for k,v in data.items()}
    with open(sys.argv[1], 'w') as f:
        json.dump(jData, f)
