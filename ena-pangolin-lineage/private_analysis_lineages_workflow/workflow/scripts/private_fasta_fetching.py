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


import argparse, os
import subprocess
import sys
import requests
import json
import pandas as pd
parser = argparse.ArgumentParser(prog='private_fasta_fetching.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |		  European Nucleotide Archive (ENA)
		part of Private analysis pangolin lineages Tool        |
        |                                                              |
        |             Tool to fetch data from ENA                      |
        + =========================================================== +  """)
parser.add_argument('-o', '--output', help='path for the output files', type=str, required=True)
args = parser.parse_args()



def private_metadata_fetch():

    print('Fetching  Metadata From Advanced Search...................................................................')
    server = "https://www.ebi.ac.uk/ena/portal/api/search"
    ext = "?dataPortal=pathogen&result=analysis&query=analysis_type%3D%22COVID19_CONSENSUS%22&fields=analysis_accession%2Csample_accession%2Csubmitted_ftp&dccDataOnly=true&format=json"
    command = requests.get(server + ext , auth=("dcc_walton","aJnN4iV5") , headers={"Content-Type": "application/json"})
    status = command.status_code
    if status == 500:
        sys.stderr.write("Attention: Internal Server Error, the process has stopped and skipped ( Data might be incomplete )\n")
    data = json.loads(command.content)
    parsed_data =[]
    for x in data:
        output = {'sample_accession':x['sample_accession'],'submitted_ftp': x['submitted_ftp']}
        parsed_data.append(output)

    parsed_data_df = pd.DataFrame(parsed_data)

    print(parsed_data_df)
    return parsed_data_df


def pulling_private_consensus (df):
    print('Pulling private fasta...................................................................')
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for url in df['submitted_ftp']:
        url_file = url.strip("ftp.sra.ebi.ac.uk").split("/")
        if url_file != [""]:
            print(url_file)
            print(url_file[4])
            if url == 'submitted_ftp':
                continue
            if not os.path.exists(f'{outdir}/{url_file[4].strip(":")}'):
                command = f'lftp -c "open ftp://dcc_walton:aJnN4iV5@ftp.dcc-private.ebi.ac.uk; get {url.strip("ftp.sra.ebi.ac.uk")} -o {outdir}"'
                sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = sp.communicate()
                sys.stderr.write(out.decode())
                sys.stderr.write(err.decode())
                stdoutOrigin = sys.stdout



##############################
#           MAIN             #
#                            #
##############################

private_metadata = private_metadata_fetch()

pulling_private_consensus(private_metadata)

f = open(f"{args.output}/end.txt", "a")
f.close()
