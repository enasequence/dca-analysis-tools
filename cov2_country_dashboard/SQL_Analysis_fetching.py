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
import datetime
from db_connect import DB_connect

parser = argparse.ArgumentParser(prog='SQL.Analysis_fetching.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) Dashboard Tool  |
        |                                                              |
        |                 |
        + =========================================================== +      
        """)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
parser.add_argument('-c', '--config', help='config file directory', type=str, required=True)
args = parser.parse_args()

def SQLstat_fetch_dataframe_analysis(connection):

    sql_original_analysis = pd.read_csv(f"{args.output}/SQL.Analysis.log.csv", sep=",")
    old_date_string = sql_original_analysis['last_updated'].iat[0]
    old_date_object = datetime.datetime.strptime(old_date_string, '%Y-%m-%d')
    old_date = old_date_object.strftime('%Y-%m-%d')
    #old_date = '2022-11-28'
    print(old_date)

    sys.stderr.write('Querying ERAPRO')
    c = connection.cursor()
    sql_row = []
    c.execute(f"select sa.SUBMISSION_ACCOUNT_ID, ap.PROJECT_ID, ap.project_status_id, ap.BIOSAMPLE_ID, ap.sample_status_id, ap.ANALYSIS_ID, ap.analysis_status_id, ap.FIRST_CREATED, sa.COUNTRY, ap.ANALYSIS_TYPE, ap.CENTER_NAME from SUBMISSION_ACCOUNT sa join\
    (select p.PROJECT_ID, p.STATUS_ID as project_status_id, asa.SUBMISSION_ACCOUNT_ID, asa.ANALYSIS_ID, asa.BIOSAMPLE_ID, asa.analysis_status_id, asa.FIRST_CREATED, asa.SAMPLE_ID, asa.sample_status_id, asa.ANALYSIS_TYPE, asa.CENTER_NAME from project p join\
        (select a.ANALYSIS_ID, a.BIOPROJECT_ID, a.SUBMISSION_ACCOUNT_ID, a.STATUS_ID as analysis_status_id, a.FIRST_CREATED, ass.sample_status_id, ass.BIOSAMPLE_ID, ass.SAMPLE_ID, a.ANALYSIS_TYPE, a.center_name from ANALYSIS a join\
            (select asa.ANALYSIS_ID, s.SAMPLE_ID,s.BIOSAMPLE_ID, s.STATUS_ID as sample_status_id from ANALYSIS_SAMPLE asa\
                join sample s on asa.sample_id = s.sample_id where s.tax_id in ('2697049')) ass on ass.ANALYSIS_ID = a.ANALYSIS_ID where a.last_updated > DATE '{old_date}') asa on asa.BIOPROJECT_ID = p.PROJECT_ID) ap\
                    on sa.SUBMISSION_ACCOUNT_ID = ap.SUBMISSION_ACCOUNT_ID")
    for row in c:
        sql_row.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])
    df_analysis = pd.DataFrame(sql_row, columns=['Webin Account', 'Project ID', 'Project Status ID', 'Sample ID', 'Sample Status ID', 'Analysis ID', 'Analysis Status ID', 'First Created' , 'Country', 'Analysis Type', 'Center Name'])

    updated_analysis_df = pd.concat([sql_original_analysis, df_analysis]).drop_duplicates(['Analysis ID'], keep='last').sort_values('Analysis ID')

    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d').upper()
    updated_analysis_df['last_updated'] = now_str


    updated_analysis_df.to_csv(f"{args.output}/SQL.Analysis.log.csv", index=False)
    print(df_analysis)

    return  df_analysis


def SQLstat_fetch_dataframe_sequences(connection, df_analysis):
    sys.stderr.write('Querying ENAPRO')
    c = connection.cursor()
    sql_row = []
    counter = 1
    time_counter = 1
    analysis_accession_list = []
    sequence_list=[]
    for index, row in df_analysis.iterrows():
        if row[9] not in ['COVID19_FILTERED_VCF','COVID19_CONSENSUS','PATHOGEN_ANALYSIS']:
            print(row[9])
            sequence_list.append(row)
    sequence_df = pd.DataFrame(sequence_list)
    print(sequence_df)
    for accession in df_analysis['Analysis ID']:
        analysis_accession_list.append(accession)
        counter += 1
        time_counter +=1
        if counter%1000 == 0:
            c.execute(f"select ASSEMBLY_ID, GC_ID, STATUS_ID as GCA_status_id, CHROMOSOME_ACC_RANGE, WGS_ACC from DATALIB.GCS_ASSEMBLY where ASSEMBLY_ID in {tuple(analysis_accession_list)}")
            for row in c:
                sql_row.append([row[0], row[1], row[2], row[3], row[4]])
            df_sequences = pd.DataFrame(sql_row, columns=['Analysis ID', 'GC_ID', 'GC Status ID', 'Sequence Accessions Range', 'WGS ID'])
            analysis_accession_list =[]
            print(df_sequences)
    if analysis_accession_list:
        c.execute(f"select ASSEMBLY_ID, GC_ID, STATUS_ID as GCA_status_id, CHROMOSOME_ACC_RANGE, WGS_ACC from DATALIB.GCS_ASSEMBLY where ASSEMBLY_ID in {tuple(analysis_accession_list)}")
        for row in c:
            sql_row.append([row[0], row[1], row[2], row[3], row[4]])
        df_sequences = pd.DataFrame(sql_row,
                                    columns=['Analysis ID', 'GC_ID', 'GC Status ID', 'Sequence Accessions Range', 'WGS ID'])
    print(df_sequences)

    sql_original_sequence = pd.read_csv(f"{args.output}/SQL.Sequence.log.csv", sep=",")
    updated_sequence_df = pd.concat([sql_original_sequence, df_sequences]).drop_duplicates(['Analysis ID'],
                                                                                          keep='last').sort_values('Analysis ID')

    #sql_original_sequence.set_index('Analysis ID', inplace=True)
    #sql_original_sequence.update(df_sequences.set_index('Analysis ID'))
    #sql_original_sequence.reset_index()
    updated_sequence_df.to_csv(f"{args.output}/SQL.Sequence.log.csv", index=False)

    return df_sequences

######################
##       MAIN       ##
##                  ##
######################

db_connect_era = DB_connect('ERAPRO', args.config).setup_connection()
db_connect_ena = DB_connect('ENAPRO', args.config).setup_connection()

df_analysis= SQLstat_fetch_dataframe_analysis(db_connect_era)
df_sequences = SQLstat_fetch_dataframe_sequences(db_connect_ena, df_analysis)

sys.stderr.write('***************** END *****************')

