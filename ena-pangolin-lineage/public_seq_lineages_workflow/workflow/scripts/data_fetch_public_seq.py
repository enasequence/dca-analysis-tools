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
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
parser = argparse.ArgumentParser(prog='pulling_fasta.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) data flow monitoring Tool  |
        |                                                              |
        |             Tool to to fetch data from NCBI or ENA           |
        + =========================================================== +  """)
parser.add_argument('-f', '--file', help='Fasta accessions file directory', type=str, required=True)
parser.add_argument('-num', '--number', help='Max Number of the multifasta file output required', type=str, required=True)
parser.add_argument('-o', '--output', help='Fasta files output directory', type=str, required=True)
args = parser.parse_args()


def divide_chunks(l, n):

    for i in range(0, len(l), n):
        yield l[i:i + n]



def API_calling (dataInput):
    server = "https://www.ebi.ac.uk/ena/browser/api/fasta/"
    ext = f"{dataInput}"
    # logging.basicConfig(level=logging.DEBUG)
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    command = session.get(server + ext, headers={"Content-Type": "text/tab-separated-values"},
                          stream=True)
    status = command.status_code
    print(status)
    data = command.content.decode('ISO-8859-1')

    return data



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
    fasta_temp_list =[]
    for accession in accession_df['accession']:
        if accession != 'accession':
            counter += 1
            if extn >= int(args.number):
                continue
            fasta_acc.append(accession)
            fasta_temp_list.append(accession)

            if counter >= number_fasta_seq:
                if len(fasta_temp_list) >= 500:
                    fasta_temp_list_divided = divide_chunks(fasta_temp_list, 500)
                    for fastaList in fasta_temp_list_divided:
                        modifiedFasta_list = ','.join([str(element) for element in fastaList])
                        data = API_calling(modifiedFasta_list)
                        with open(f"{outdir}/multifasta_{extn}.fasta", "a") as f:
                            f.write(data)
                else:       
                    modifiedFasta_list = ','.join([str(element) for element in fasta_temp_list])
                    print(len(fasta_temp_list))
                    data = API_calling(modifiedFasta_list)
                    with open(f"{outdir}/multifasta_{extn}.fasta", "a") as f:
                        f.write(data)
                fasta_temp_list = []
                counter = 0
                extn += 1

    if extn <= int(args.number):
        for accession in accession_df['accession']:
            if accession not in fasta_acc:
                if accession !='accession':
                    fasta_acc.append(accession)
                    data = API_calling(accession)
                    with open(f"{outdir}/multifasta_{extn}.fasta", "a") as f:
                        f.write(data)

    print(f"{extn} Multifasta Files have been Created ****************\n")


#############################
#                           #
#           MAIN            #
#                           #
#############################

fetching_fasta_files()
