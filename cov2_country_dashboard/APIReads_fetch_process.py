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
from merger import Merger
parser = argparse.ArgumentParser(prog='APIReads_fetch_process.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |   European Nucleotide Archive (ENA) Dashboard Tool           |
        |                                                              |
        |                 |
        + =========================================================== +      
        """)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
parser.add_argument('-f', '--file', help='Analysis and Sequence directory', type=str, required=True)
args = parser.parse_args()

def grep_INSDC_sequences(API_data):
    df = pd.DataFrame.from_dict(API_data, orient='columns')
    print(df)
    df['country'] = df['country'].str.split(':').str[0]
    NCBI_list=[]
    DDBJ_list=[]
    for index, row in df.iterrows():
        print(row[0])
        #if key == 'accession':
        if fnmatch.fnmatch(row[0], '[ADGJKLMNPQRSVWX]*'):
            NCBI_list.append(row)
        if fnmatch.fnmatch(row[0], '[BEIT]*'):
            DDBJ_list.append(row)

    NCBI_list.extend(DDBJ_list)
    INSDC_list = NCBI_list

    print(INSDC_list)
    return INSDC_list


def fetching_seq_data():
    server = "https://www.ebi.ac.uk/ena/portal/api/search"
    ext = "?result=sequence&query=tax_tree(2697049)&fields=accession,first_public,country&format=json&limit=0"
    command = requests.get(server + ext, headers={"Content-Type": "application/json"})
    data = json.loads(command.content)
    database='sequence'
    return [data, database]

def fetching_reads_data():
    server = "https://www.ebi.ac.uk/ena/portal/api/search"
    ext = r"?result=read_experiment&query=tax_tree(2697049)&fields=accession,first_public,country&format=json&limit=0"
    command = requests.get(server + ext, headers={"Content-Type": "application/x-www-form-urlencoded"}, stream=True)
    read_data = json.loads(command.content)
    database = 'reads'
    return [read_data, database]

def dataframe (data, database):
    df = pd.DataFrame.from_dict(data, orient='columns')
    df['country'] = df['country'].str.split(':').str[0]
    df.sort_values('country')
    df1=df.rename(columns={'first_public': 'Submission Date'})
    filtered_df = df1.groupby(['Submission Date','country']).size().reset_index(name='Submissions')
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    old_name = f'{outdir}/API.{database}.output.recent.csv'
    if os.path.exists(old_name):
        new_name = f'{outdir}/API.{database}.output.old.csv'
        os.rename(old_name, new_name)
    filtered_df.to_csv(old_name, index=False)
    return filtered_df


def stat_dataframe_reads (data, sql_output, database):
    df = pd.DataFrame.from_dict(data, orient='columns')
    df['country'] = df['country'].str.split(':').str[0]
    sql_api_join= pd.merge(sql_output, df[['experiment_accession', 'country']], on='experiment_accession', how='left')
    sql_api_join['Country'] = sql_api_join['Country'].fillna(sql_api_join['country'])
    sql_api_join.drop(['country'], inplace=True, axis=1)
    print(sql_api_join)
    print(sql_api_join.keys())
    #print(sql_api_join[1])
    sql_api_join[["Project Status ID","Sample Status ID","RUN Status ID", "Experiment Status ID"]].astype(int)
    #sql_api_join = sql_api_join[['Webin Account', 'Project ID', 'Project Status ID', 'Sample ID', 'Sample Status ID', 'RUN ID', 'RUN Status ID', 'First Created', 'experiment_accession', 'Experiment Status ID','Center Name', 'Country']]
    #sql_api_join.astype({"Project Status ID": 'int' ,"Sample Status ID": 'int',"RUN Status ID": 'int', "Experiment Status ID": 'int'})
    print(sql_api_join.dtypes)
    merger = Merger(sql_api_join.astype(str), database)
    sql_api_join_read_webin = merger[0]
    sql_api_join_read_webin.to_csv(f"{args.output}/SQL-API.{database}_webin.log.csv", index=False)
    sql_api_join_read_project = merger[1]
    sql_api_join_read_project.to_csv(f"{args.output}/SQL-API.{database}_project.log.csv", index=False)
    center_name_grouped = merger[2]
    print(center_name_grouped)
    center_name_grouped.to_csv(f"{args.output}/SQL-API.{database}_center_names.log.csv",
                                     index=False)

###########################################
#                                         #
#                 MAIN                    #
#                                         #
###########################################
print('Fetching Reads Data  ........\n')
data_reads = fetching_reads_data()
dataframe_reads = dataframe(data_reads[0],data_reads[1])

print('Fetching Sequences Data  ........\n')
data_seq = fetching_seq_data()
dataframe_seq = dataframe(data_seq[0],data_seq[1])

#sys.stderr.write("Connecting to ERAPRO...\n")
#db_conn_erapro = setup_connection('ERAPRO')
# fetching reads
sys.stderr.write("Querying ERAPRO ..........\n")
#sql_output= SQLstat_fetch_dataframe(db_conn_erapro)
sql_output = pd.read_csv(f"{args.file}/SQL.Reads.log.csv", sep=",")#, dtype={"Webin Account": "string", "Project ID": "string", "Project Status ID": int, "Sample ID": "string", "Sample Status ID": int, "RUN ID": "string", "RUN Status ID": int, "First Created": "string", "experiment_accession":"string", "Experiment Status ID": int, "Center Name":"string", "Country": "string"})
stat_dataframe_reads(data_reads[0], sql_output,data_reads[1])
# fetching analysis data
#sql_output_analysis= SQLstat_fetch_dataframe_analysis(db_conn_erapro)
#fetching sequences based on the analysis
#sys.stderr.write("Connecting to ENAPRO...\n")
#db_conn_enapro = setup_connection('ENAPRO')
#sql_output_seq= SQLstat_fetch_dataframe_sequences(db_conn_enapro,sql_output_analysis)

#Fetching INSDC data
INSDC_data = grep_INSDC_sequences(data_seq[0])
INSDC_df = dataframe(INSDC_data, 'INSDC_seq')



sys.stderr.write("*************END*************\n")
