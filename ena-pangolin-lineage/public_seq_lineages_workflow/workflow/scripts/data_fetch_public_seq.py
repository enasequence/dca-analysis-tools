# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse, hashlib, os, subprocess, sys, time
from os import listdir
import os
import shutil
import sys
import shlex
import subprocess
import requests, sys
import re
import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import pandas as pd
import math
from dateutil.relativedelta import relativedelta, MO
parser = argparse.ArgumentParser(prog='pulling_fasta.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |               European Nucleotide Archive (ENA)
		  part of Public sequence pangolin lineages Tool       |
        |                                                              |
        |             Tool to to fetch data from ENA                   |
        + =========================================================== +  """)
parser.add_argument('-f', '--file', help='Fasta accessions file directory', type=str, required=True)
parser.add_argument('-num', '--number', help='Max Number of the multifasta file output required', type=str, required=True)
parser.add_argument('-o', '--output', help='Fasta files output directory', type=str, required=True)
args = parser.parse_args()

def fetching_fasta_files ():
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    accession_df = pd.read_csv(args.file, sep=",", header=None, names=['accession', 'date'])
    counter = 0
    extn = 1
    total_num = len(accession_df['accession']) - 1
    number_fasta_seq = math.trunc(total_num / int(args.number))
    print(f"Found {total_num} fasta files in {args.file} - writing {number_fasta_seq} sequences to each multifasta file, the rest -if exist- will be merged with the last file **************\n")
    fasta_acc = []
    for accession in accession_df['accession']:
        counter += 1
        if extn >= int(args.number):
            continue
        fasta_acc.append(accession)
        server = "https://www.ebi.ac.uk/ena/browser/api/fasta/"
        ext = f"{accession}"
        command = requests.get(server + ext, headers={"Content-Type": "text/tab-separated-values"},stream=True)
        status = command.status_code
        data = command.content.decode('ISO-8859-1')
        with open(f"{outdir}/multifasta_{extn}.fasta", "a") as f:
            f.write(data)

        if counter >= number_fasta_seq:
            counter = 0
            extn += 1

    if extn <= int(args.number):
        for accession in accession_df['accession']:
            if accession not in fasta_acc:
                fasta_acc.append(accession)
                server = "https://www.ebi.ac.uk/ena/browser/api/fasta/"
                ext = f"{accession}"
                command = requests.get(server + ext, headers={"Content-Type": "text/tab-separated-values"}, stream=True)
                status = command.status_code
                data = command.content.decode('ISO-8859-1')
                with open(f"{outdir}/multifasta_{extn}.fasta", "a") as f:
                    f.write(data)

    print(f"{extn} Multifasta Files have been Created ****************\n")


#############################
#                           #
#           MAIN            #
#                           #
#############################

fetching_fasta_files()
