# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse, hashlib, os, subprocess, sys, time
from os import listdir
import gzip
import fnmatch #module for unix style pattern matching
import math
import os
parser = argparse.ArgumentParser(prog='create_multifasta.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  		European Nucleotide Archive (ENA)
		part of Private analysis pangolin lineages Tool       |
        |                                                              |
        |             Tool to create multifasta files                 |
        + =========================================================== +  """)

parser.add_argument('-f', '--file', help='Fasta files input directory', type=str, required=True)
parser.add_argument('-o', '--output', help='multiFasta files output directory', type=str, required=True)
parser.add_argument('-num', '--number', help='Max Number of the multifasta file output required', type=str, required=True)
args = parser.parse_args()

def read_fasta():
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    total_files = os.listdir(args.file)
    number_fasta_seq = math.trunc(len(total_files)/int(args.number))
    print(f"Found {len(total_files)} fasta files in {args.output} - writing {number_fasta_seq} sequences to each multifasta file, the rest-if exist- will be merged with the last file **************\n")
    index = 0
    ext = 1
    fasta_list = []
    for f in listdir(args.file):
        if fnmatch.fnmatch(f, '*.fasta.gz'):
            index += 1
            if ext >= int(args.number):
                continue
            fasta_list.append(f)
            fp = open(f'{outdir}/multifasta_{ext}.fasta', 'ab')
            with gzip.open(f'{args.file}/{f}','rb') as f_in:
                content = f_in.read()
                fp.write(content)
            fp.close()
            if index >= number_fasta_seq:
                index = 0
                ext +=1
    if ext <= int(args.number):
        for f in listdir(args.file):
            if fnmatch.fnmatch(f, '*.fasta.gz'):
                if f not in fasta_list:
                    fp = open(f'{outdir}/multifasta_{ext}.fasta', 'ab')
                    with gzip.open(f'{args.file}/{f}', 'rb') as f_in:
                        content = f_in.read()
                        fp.write(content)
                    fp.close()


    print(f"{ext} Multifasta Files have been Created ****************\n")

#######################
#                     #
#         MAIN        #
#######################

#os.remove(f"{args.file}/end.txt")

read_fasta()

#f = open(f"{args.output}/end.txt", "a")
#f.close()

