#!/usr/bin/env python3.8

# Copyright [2020] EMBL-European Bioinformatics Institute
#
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
import pandas as pd
import requests
import json
import cx_Oracle
import fnmatch
from db_connect import DB_connect

parser = argparse.ArgumentParser(prog='SQL.Reads_fetching.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |   European Nucleotide Archive (ENA) Dashboard Tool          |
        |                                                              |
        |                 |
        + =========================================================== +      
        """)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
parser.add_argument('-c', '--config', help='config file directory', type=str, required=True)
args = parser.parse_args()

def SQLstat_fetch_dataframe(connection):
   # This Part is for querying ERAPRO
    sys.stderr.write('Querying ERAPRO')
    c = connection.cursor()
    sql_row = []
    c.execute("select sa.submission_account_id, d.project_id,d.status_id, d.biosample_id, d.status_sample, d.run_id, d.status_run, d.first_created, d.experiment_id, d.status_exp, d.center_name ,sa.country from\
                (select sp.submission_account_id, c.project_id, c.status_id, c.status_run, sp.biosample_id, sp.status_id as status_sample, c.run_id, c.experiment_id, c.status_exp, c.center_name, c.first_created from\
                (select b.project_id, b.status_id, es.sample_id, b.run_id, b.status_run, b.experiment_id, b.status_exp, b.center_name, b.first_created from\
                (select a.project_id, a.status_id, r.run_id, r.status_id as status_run, r.experiment_id, a.status_exp, r.CENTER_NAME as center_name, r.FIRST_CREATED as first_created from\
                (select st.project_id, st.status_id, ex.experiment_id, ex.status_id as status_exp from experiment ex left join study st on ex.study_id =st.study_id) a\
                join run r on a.experiment_id = r.experiment_id) b join experiment_sample es on es.experiment_id = b.experiment_id) c\
                join sample sp on c.sample_id = sp.sample_id where sp.tax_id in ('2697049')) d left join submission_account sa on sa.submission_account_id = d.submission_account_id")
    for row in c:
        sql_row.append([row[0],row[1],row[2], row[3],row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]])
    df = pd.DataFrame(sql_row, columns= ['Webin Account', 'Project ID', 'Project Status ID', 'Sample ID', 'Sample Status ID', 'RUN ID', 'RUN Status ID', 'First Created', 'experiment_accession', 'Experiment Status ID','Center Name', 'Country'])
    df.to_csv(f"{args.output}/SQL.Reads.log.csv", index=False)

    return df


#################
#    MAIN     ###
#             ###
#################

db_connect = DB_connect('ERAPRO', args.config).setup_connection()
SQLstat_fetch_dataframe(db_connect)
sys.stderr.write('******************END**********************')