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
from dateutil.relativedelta import relativedelta, MO
parser = argparse.ArgumentParser(prog='pulling_fasta.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |            European Nucleotide Archive (ENA)
		part of Public analysis pangolin lineages Tool        |
        |                                                              |
        |             Tool to to fetch consensus data from ENA           |
        + =========================================================== +  """)
parser.add_argument('-o', '--output', help='Fasta files output directory', type=str, required=True)
parser.add_argument('-p', '--project', help='projects ids (separated with comma without spaces )', type=str, required=True)
args = parser.parse_args()

def project_parsing():
    study_accession = [f'study_accession%3D%22{i}' for i in args.project.split(',')]
    length= len(study_accession)
    counter = 0
    study_accession_updated =[]
    for x in study_accession:
        counter += 1
        if counter == length:
            study_accession_updated.append(f'{x}')
        else:
            study_accession_updated.append(f'{x}%22%20OR%20')
        study_acc_final = (''.join(study_accession_updated))

    return study_acc_final





def public_metadata_fetch():
    study_acc = project_parsing()
    print('Fetching  Metadata From Advanced Search...................................................................')
    server = "https://www.ebi.ac.uk/ena/portal/api/search"
    ext = f"?result=analysis&query=tax_eq(2697049%20)%20AND%20({study_acc}%22)&fields=submitted_ftp&limit=0&format=json"
    command = requests.get(server + ext , headers={"Content-Type": "application/json"})
    status = command.status_code
    if status == 204:
        sys.stderr.write(
            f"Attention: The Assigned Project(s) {args.project} has(have) no data\nExiting.......")
        exit(1)
    if status == 500:
        sys.stderr.write("Attention: Internal Server Error, the process has stopped and skipped ( Data might be incomplete )\n")
    data = json.loads(command.content)
    parsed_data =[]
    for x in data:
        output = {'analysis_accession':x['analysis_accession'],'submitted_ftp': x['submitted_ftp']}
        parsed_data.append(output)

    parsed_data_df = pd.DataFrame(parsed_data)

    print(parsed_data_df)
    return parsed_data_df

def pulling_public_consensus (df):
    print('Pulling public fasta...................................................................')
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for url in df['submitted_ftp']:
        if url == 'submitted_ftp':
            continue
        url_file = url.strip("ftp.sra.ebi.ac.uk").split("/")
        sub_outdir = f"{outdir}/{url_file[2]}"
        if not os.path.exists(sub_outdir):
            os.mkdir(sub_outdir)
        if not os.path.exists(f'{sub_outdir}/{url_file[4].strip(":")}'):
            command = f'lftp -c "open ftp://ftp.sra.ebi.ac.uk; get {url.strip("ftp.sra.ebi.ac.uk")} -o {sub_outdir}"'
            sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = sp.communicate()
            sys.stderr.write(out.decode())
            sys.stderr.write(err.decode())
            stdoutOrigin = sys.stdout



metadata_df = public_metadata_fetch()

pulling_public_consensus(metadata_df)

f = open(f"{args.output}/end.txt", "a")
f.close()
