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
__author__ = "Ahmad Zyoud"

import argparse, hashlib, os, subprocess, sys, time
import sys
import shlex
import subprocess
import requests, sys
import re
import requests
import json
from datetime import datetime
import cx_Oracle
from getpass import getpass
import collections
import numpy as np
import pandas as pd
import datetime
import configparser
import fnmatch


parser = argparse.ArgumentParser(prog='duplication_scan.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) analysis duplication monitoring Tool |
        |                                                              |
        |     
        + =========================================================== +
This script is used to analyse the data from NCBI and ENA that been produced by data_fetch_script.py.        
        """)
parser.add_argument('-o', '--output', help='path for the output folder', type=str, required=True)
parser.add_argument('-c', '--config', help='config file path', type=str, required=True)
args = parser.parse_args()

# generate and create the output directory
def create_outdir():
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y_%H-%M-%S")
    outdir = f"{args.output}/duplication_public_output_logs_{now_str}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    return outdir

"""
Setup the connection to ENAPRO and ERAPRO. 
"""
def setup_connection():
    config = configparser.ConfigParser()
    config.read(args.config)
    oracle_usr, oracle_pwd = [config['ERAPRO_DETAILS']['userName'],
                              config['ERAPRO_DETAILS']['password']]  # get_oracle_usr_pwd
    client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
    if not client_lib_dir or not os.path.isdir(client_lib_dir):
        sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
        exit(1)
    cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
    connection = None
    try:
        dsn = cx_Oracle.makedsn(config['ERAPRO_DETAILS']['host'], config['ERAPRO_DETAILS']['port'], service_name=config['ERAPRO_DETAILS']['serviceName'])
        connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8")
        return connection
    except cx_Oracle.Error as error:
        print(error)

def fetch_details(connection):
    config = configparser.ConfigParser()
    config.read(args.config)
    sys.stderr.write("Processing Stage 1 ..........\n")
    sys.stderr.write("scan for files duplication ..........\n")
    c = connection.cursor()
    dict = {}
    value =[]
    c.execute(
        f"select w.upload_file_path, count(w.upload_file_path) from webin_file w join (select * from analysis where bioproject_id in ({config['DataHub_Projects']['projects']}) and status_id !=5 and status_id !=3) a \
         on a.analysis_id = w.data_file_owner_id GROUP BY w.upload_file_path HAVING COUNT(w.upload_file_path) > 1")
    for row in c:
        value.append(row [0])

    dict['file_name'] = value
    df = pd.DataFrame.from_dict (dict, orient='columns', dtype=None, columns=None)

    return df

def tarFiles_duplicates_calling (connection):
    config = configparser.ConfigParser()
    config.read(args.config)
    sys.stderr.write("PATHOGEN_ANALYSIS type files fetching ..........\n")
    c = connection.cursor()

    value = []
    c.execute(
        f"select run_id, a.analysis_id, a.status_id, a.first_created, a.audit_time, wf.UPLOAD_FILE_PATH, a.bioproject_id, wf.bytes, wf.checksum from WEBIN_FILE wf join\
    (select ANALYSIS_ID, STATUS_ID, FIRST_CREATED,AUDIT_TIME, BIOPROJECT_ID, extractValue(ANALYSIS_XML, 'ANALYSIS_SET/ANALYSIS/RUN_REF/IDENTIFIERS/PRIMARY_ID') as run_id\
    from analysis where bioproject_id in ({config['DataHub_Projects']['projects']})\
    and status_id !=5 and STATUS_ID !=3 and ANALYSIS_TYPE = 'PATHOGEN_ANALYSIS') a on wf.DATA_FILE_OWNER_ID = a.ANALYSIS_ID"
    )
    for row in c:
        value.append(row)
    df = pd.DataFrame(value)
    df.columns = ['run_id', 'Accession', 'Status_id', 'First_created', 'Audit_time', 'File_name', 'Project_id', 'File_Size', 'Checksum']

    return df


def tarFiles_duplicates_processing(df):
    sys.stderr.write("PATHOGEN_ANALYSIS type files fetching ..........\n")
    df_grouped = df.groupby('run_id').size()
    df_filtered = df_grouped[df_grouped > 3].reset_index(name='counts')
    df_merged = df_filtered.merge(df, how= 'inner', on= 'run_id')
    df_merged = df_merged.drop('counts', axis=1)
    return (df_merged)

def tarFiles_processing (df_merged):
    sys.stderr.write("duplicated Tar files fetching ..........\n")
    tarFile_list =[]
    for index, row in df_merged.iterrows():
        if fnmatch.fnmatch(row['File_name'], '*tar.gz'):
            tarFile_list.append(row)
    tarFile_df = pd.DataFrame(tarFile_list)
    tarFile_df.columns = ['run_id', 'Accession', 'Status_id', 'First_created', 'Audit_time', 'File_name', 'Project_id', 'File_Size', 'Checksum']

    return tarFile_df


def stage2_processing(connection, df):
    c = connection.cursor()
    sys.stderr.write("Processing Stage 2 ..........\n")
    f = open(f"{outdir}/duplicated_analysis_details.log.txt", "w")
    header = "\t".join(['Accession', 'Status_id', 'First_created', 'Audit_time', 'File_name', 'Project_id', 'File_Size', 'Checksum'])
    f.write(str(header) + "\n")
    for file_name in df['file_name']:
        if file_name == 'file_name':
            continue
        else:
            c.execute(
                f"select a.analysis_id, a.status_id, a.first_created, a.audit_time, w.upload_file_path, a.bioproject_id, w.bytes, w.checksum\
                from analysis a join (select * from webin_file where\
                upload_file_path in ('{file_name}')) w\
                on a.analysis_id = w.data_file_owner_id where a.status_id !=5 and a.status_id !=3")
            for row in c:
                f.write(str(row[0]) + "\t" + str(row[1]) + "\t" + str(row[2]) + "\t" + str(row[3]) + "\t" + str(row[4]) + "\t" + str(row[5]) + "\t" + str(row[6]) + "\t" + str(row[7]) + "\n")
    f.close()

def drop_duplicate(df):
    sys.stderr.write("Filtering Duplicates ..........\n")
    df['First_created'] = pd.to_datetime(df['First_created'])
    cancelled = []
    ignore_list = []
    suppressed = []
    ignore = []
    for row in df.to_dict('records'):
        if row['Status_id'] == 2:
            cancelled.append(row)
            ignore_list.append(row['File_name'])

    for x in df.to_dict('records'):
        if x['Status_id'] == 4 and not x['File_name'] in ignore_list:
            suppressed.append(x)


    for i in df.to_dict('records'):
        if i['Status_id'] == 4 and i['File_name'] in ignore_list:
            ignore.append(i)


    cancelled_df = pd.DataFrame(cancelled)
    suppressed_df = pd.DataFrame(suppressed)
    ignore_df = pd.DataFrame(ignore)
    df_addition = ignore_df.loc[ignore_df.duplicated(subset=['File_name'], keep = False)]
    df_filtered = pd.concat([suppressed_df, df_addition])

    if not df_filtered.empty:
        df_processed = df_filtered.sort_values('First_created').drop_duplicates('File_name', keep='last')
        df_processed.to_csv(f'{outdir}/duplicates_to_be_suppressed.log.txt', index=False, sep='\t', mode='w')
        sys.stderr.write(f"{len(df_processed)} Public Duplicated Data were Found, please check {outdir}/duplicates_to_be_suppressed.log.txt")
    if not cancelled_df.empty:
        cancelled_df.to_csv(f'{outdir}/duplicates_to_be_cancelled.log.txt', index=False, sep='\t', mode='w')
        sys.stderr.write(f"{len(cancelled_df)} Private Duplicated Data were Found, please check {outdir}/duplicates_to_be_cancelled.log.txt")
    sys.stderr.write("........................ END ...................\n")

#############
##  MAIN   ##
#############
#Calling the create_outdir module
outdir = create_outdir()

#Connecting to ERAPRO
sys.stderr.write("Connecting to ERAPRO...\n")
db_conn = setup_connection()
sys.stderr.write("Querying ERAPRO ..........\n")
df = fetch_details(db_conn)
stage2_processing(db_conn,df)
tarfiles_df = tarFiles_duplicates_calling(db_conn)
tarFiles_merged = tarFiles_duplicates_processing(tarfiles_df)
tarFiles_merged.to_csv(f"{outdir}/duplicated_analysis_details_PATHOGEN_ANALYSIS.log.txt", index=False)
tarFiles_processed = tarFiles_processing(tarFiles_merged)
if not tarFiles_processed.empty:
    tarFiles_processed.to_csv(f'{outdir}/tarFiles_duplicates_to_be_suppressed.log.txt', index=False)
    sys.stderr.write(f"{len(tarFiles_processed)} Tar Files Duplicated Data were Found, please check {outdir}/tarFiles_duplicates_to_be_suppressed.log.txt\n")
duplicat_details =pd.read_csv (f"{outdir}/duplicated_analysis_details.log.txt", sep="\t", header=0)
drop_duplicate(duplicat_details)


