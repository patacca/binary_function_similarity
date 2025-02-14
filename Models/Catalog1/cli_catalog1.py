#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Code for the USENIX Security '22 paper:                                   #
#  How Machine Learning Is Solving the Binary Function Similarity Problem.   #
#                                                                            #
#  MIT License                                                               #
#                                                                            #
#  Copyright (c) 2019-2022 Cisco Talos                                       #
#                                                                            #
#  Permission is hereby granted, free of charge, to any person obtaining     #
#  a copy of this software and associated documentation files (the           #
#  "Software"), to deal in the Software without restriction, including       #
#  without limitation the rights to use, copy, modify, merge, publish,       #
#  distribute, sublicense, and/or sell copies of the Software, and to        #
#  permit persons to whom the Software is furnished to do so, subject to     #
#  the following conditions:                                                 #
#                                                                            #
#  The above copyright notice and this permission notice shall be            #
#  included in all copies or substantial portions of the Software.           #
#                                                                            #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,           #
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF        #
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND                     #
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE    #
#  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION    #
#  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION     #
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.           #
#                                                                            #
#  cli_catalog1.py - Call IDA_catalog1 IDA script.                           #
#                                                                            #
##############################################################################

import click
import json
import subprocess
import time

from os import getenv
from os.path import abspath
from os.path import dirname
from os.path import isfile
from os.path import join
from multiprocessing import Pool

IDA_PATH = getenv("IDA_PATH", "/home/user/idapro-7.3/idat64")
IDA_PLUGIN = join(dirname(abspath(__file__)), 'IDA_catalog1.py')
REPO_PATH = dirname(dirname(dirname(abspath(__file__))))
LOG_PATH = "catalog1_log.txt"
N_JOBS = 32  # Use all the resources available


def run_process(idb_rel_path, json_path, sig_size, output_csv_s):
    """
    Run the IDA script and returns -1 if there was an error and 1 if it was a success
    """

    print("\n[D] Processing: {}".format(idb_rel_path))

    # Convert the relative path into a full path
    idb_path = join(REPO_PATH, idb_rel_path)
    print("[D] IDB full path: {}".format(idb_path))

    if not isfile(idb_path):
        print("[!] Error: {} does not exist".format(idb_path))
        return -1

    cmd = [IDA_PATH,
           '-A',
           '-L{}'.format(LOG_PATH),
           '-S{}'.format(IDA_PLUGIN),
           '-Ocatalog1:{}:{}:{}:{}'.format(
               json_path,
               idb_rel_path,
               sig_size,
               output_csv_s),
           idb_path]

    print("[D] cmd: {}".format(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    if proc.returncode == 0:
        print("[D] {}: success".format(idb_path))
        return 1
    else:
        print("[!] Error in {} (returncode={})".format(idb_path, proc.returncode))
        return -1

@click.command()
@click.option('-j', '--json-path', required=True,
              help='JSON file with selected functions.')
@click.option("-o", "--output-csv", required=True,
              help="Path to the output CSV file")
def main(json_path, output_csv):
    """Call IDA_catalog1 IDA script."""
    if not isfile(IDA_PATH):
        print("[!] Error: IDA_PATH:{} not valid".format(IDA_PATH))
        print("Use 'export IDA_PATH=/full/path/to/idat64'")
        exit(1)

    print("[D] JSON path: {}".format(json_path))
    print("[D] Output CSV: {}".format(output_csv))

    if not isfile(json_path):
        print("[!] Error: {} does not exist".format(json_path))
        exit(1)

    with open(json_path) as f_in:
        jj = json.load(f_in)

    for sig_size in [16, 32, 64, 128]:
        print("[D] Catalog1 with {} permutations".format(sig_size))
        output_csv_s = output_csv.replace(".csv", "")
        output_csv_s += "_{}.csv".format(sig_size)

        success_cnt, error_cnt = 0, 0
        start_time = time.time()

        with Pool(N_JOBS) as pool:
            res = pool.starmap(run_process, ((idb_rel_path, json_path, sig_size, output_csv_s) for idb_rel_path in jj.keys()))
        for r in res:
            if r > 0:
                success_cnt += r
            else:
                error_cnt -= r

        end_time = time.time()
        print("[D] Elapsed time: {}".format(end_time - start_time))
        with open(LOG_PATH, "a+") as f_out:
            f_out.write("elapsed_time: {}\n".format(end_time - start_time))

        print("\n# IDBs correctly processed: {}".format(success_cnt))
        print("# IDBs error: {}".format(error_cnt))

if __name__ == '__main__':
    main()
