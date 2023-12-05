#!/usr/bin/env python
import glob, re, sys
import argparse, hashlib, os, subprocess, sys, time
import fnmatch

parser = argparse.ArgumentParser(prog='filtration_merging.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + =================================================================================================================================== +
        |                           European Nucleotide Archive (ENA)                                               |
        |                                                                                                                                     |
        |                           |
        + =================================================================================================================================== +
        """)
parser.add_argument('-f', '--file', help='path for the list', type=str, required=True)
args = parser.parse_args()


def compare_and_filter():
    wildcard = args.file
    all_files = [f.path for f in os.scandir(wildcard) if fnmatch.fnmatch(f, '*.csv')]
    new_file = max(all_files, key=os.path.getctime)

    linked_file = os.readlink(f'{wildcard}/public_sequence_pango_lineages.csv')
    linked_file = f'{wildcard}/{os.path.basename(linked_file)}'
    files = [linked_file,new_file]
    print(files)
    uniq_accs = {}
    for i in files:
        with open(i, "r") as file:
            header = file.readline()
            for line in file:
                seq_acc_rx = re.search('ENA\|(.+)\|', line)
                if seq_acc_rx:
                    seq_acc = seq_acc_rx.group(1)
                    uniq_accs[seq_acc] = line.strip()

    c = 0
    with open(f'{args.file}/public_seq_pango_lineages_updated_combined_filtrered_{os.path.basename(new_file).lstrip("public_seq_pango_lineages_updated")}', 'a') as output:
        output.write(header)
        for k in uniq_accs.keys():
            output.write(f"{uniq_accs[k]}\n")
            c += 1
            if c % 100000 == 0:
                sys.stderr.write(f"written {c} sequences\n")



##############################

#       MAIN                 #

##############################

if __name__ == '__main__':
    compare_and_filter()
