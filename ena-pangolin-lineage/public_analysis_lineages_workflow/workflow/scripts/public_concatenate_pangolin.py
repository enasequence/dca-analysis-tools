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
import pandas as pd
import glob
import os
parser = argparse.ArgumentParser(prog='public_concatenate_pangolin.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |               European Nucleotide Archive (ENA)
	           part of Public analysis pangolin lineages Tool      |
        |                                                              |
        |             Tool to concate pangolin csv output              |
        + =========================================================== +  """)

parser.add_argument('-f', '--file', help='csv files input directory', type=str, required=True)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
args = parser.parse_args()

def concat_csv():
    files = os.path.join(args.file, "pango_lineages.*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    df_final = formatting_dataframe(df)
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y")
    df_final.to_csv(f'{args.output}/public_consensus_pango_lineages_{now_str}.csv', index=False)
    print(f'Concatenate all csv files in {args.file} into {args.output}/public_consensus_pango_lineages_{now_str}.csv')

def formatting_dataframe(df):
    run_acc_list =[]
    for row in df['taxon']:
        parsed_row = row.split('_')
        parsed_row = parsed_row[0].split(' ')
        run_acc = re.sub(r'^.*?:','', parsed_row[0])
        run_acc_list.append(run_acc)
    run_df = pd.DataFrame({'run_accession':run_acc_list})
    df = pd.concat([df, run_df], ignore_index=False, axis=1)
    who_list = []
    for row in df['scorpio_call']:
        who_parsed = str(row).split('(')
        who_list.append(who_parsed[0])
    who_df = pd.DataFrame({'who_lineage': who_list})
    df = pd.concat([df, who_df], ignore_index=False, axis=1)
    return df

concat_csv()
f = open(f"{args.file}/end_of_pangolin_workflow.txt", "w")
f.close()
