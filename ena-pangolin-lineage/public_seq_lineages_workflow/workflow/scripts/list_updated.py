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
from datetime import datetime, timedelta
import pandas as pd
import time
import math
from dateutil.relativedelta import relativedelta, MO
import json
parser = argparse.ArgumentParser(prog='list_updated.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
            |              European Nucleotide Archive (ENA)               |
        |          part of Public sequence pangolin lineages Tool       |
        |             Tool to to fetch data from ENA           |
        + =========================================================== +  """)
parser.add_argument('-f', '--old_file', help='accession file directory', type=str, required=True)
parser.add_argument('-d', '--days', help='threshold date from to be included in the output ( by days)', type=int, required=True)
parser.add_argument('-o', '--output', help='accession output directory', type=str, required=True)
args = parser.parse_args()

def upload_files ():
    accession_df = pd.read_csv(args.old_file, sep=",", header=None, names=['accession', 'date'])

    return accession_df

def formatting_dataframe (df):
    today = datetime.today()
    date_to_go = today - timedelta(days = args.days)
    print(date_to_go)
    df_list =[]
    for i in df.to_dict('records'):
        formatted_date = datetime.strptime(i['date'], "%Y-%m-%d")
        if formatted_date < date_to_go:
            continue
        else:
            dict ={"accession":i['accession'],"date":i['date']}
            df_list.append(dict)
    df_mod = pd.DataFrame(df_list)

    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    df_mod.to_csv(f"{args.output}/embl-covid19.accs_updated.txt", index=False)


#############################
#                           #
#           MAIN            #
#                           #
#############################

accessions_df = upload_files()
formatting_dataframe(accessions_df)
