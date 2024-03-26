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
__author__ = "Ahmad Zyoud"

parser = argparse.ArgumentParser(prog='analysis_bulk_suppressor.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) analysis duplication monitoring Tool |
        |                                                              |
        |     
        + =========================================================== +
This script is used to analyse the data from NCBI and ENA that been produced by data_fetch_script.py.        
        """)
parser.add_argument('-c', '--config', help='config file path', type=str, required=True)
parser.add_argument('-f', '--file', help='path for the input files', type=str, required=True)
parser.add_argument('-db', '--database', help='The dataset type, ex: sequences or reads:', type=str, required=False)
parser.add_argument('-a', '--action', help='Action type: suppress or cancel', type=str, required=False)
args = parser.parse_args()

"""
Request username and password for databases
"""
def get_oracle_usr_pwd():
    config = configparser.ConfigParser()
    config.read(args.config)
    if database.lower() == 'erapro':
        return [config['ERAPRO_DETAILS']['userName'].iloc[0], config['ERAPRO_DETAILS']['password'].iloc[0]]
    elif database.lower() == 'enapro':
        return [config['ENAPRO_DETAILS']['userName'].iloc[0], config['ENAPRO_DETAILS']['password'].iloc[0]]



"""
Setup the connection to ENAPRO and ERAPRO. 
"""
def setup_connection():
    config = configparser.ConfigParser()
    oracle_usr, oracle_pwd = get_oracle_usr_pwd()
    client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
    if database == 'enapro':
        if not client_lib_dir or not os.path.isdir(client_lib_dir):
            sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
            exit(1)
        cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
        connection = None
        try:
            dsn = cx_Oracle.makedsn(config['ENAPRO_DETAILS']['host'], config['ENAPRO_DETAILS']['port'], service_name=config['ENAPRO_DETAILS']['serviceName'])
            connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8")
            return connection
        except cx_Oracle.Error as error:
            print(error)
    else:
        if not client_lib_dir or not os.path.isdir(client_lib_dir):
            sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
            exit(1)
        cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
        connection = None
        try:
            dsn = cx_Oracle.makedsn(config['ERAPRO_DETAILS']['host'], config['ERAPRO_DETAILS']['port'], service_name=config['ERAPRO_DETAILS']['serviceName'])
            connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8", events=True)
            return connection
        except cx_Oracle.Error as error:
            print(error)

def suppression(connection, action):
    config = configparser.ConfigParser()
    c = connection.cursor()
    connection.autocommit = True
    df = pd.read_csv(args.file, sep="\t", header=None)
    rowcount = 0
    accession_list =[]
    dict ={}
    for accession in df[0]:
        c.execute(
            f"update analysis set status_id='{action}', hold_date=null, status_comment ='{config['STATUS']['statusComment']}' where analysis_id in ('{accession}')")
        rowcount = rowcount + int(c.rowcount)
        accession_list.append(accession)
    rowcount_total = 'Number of rows updated: ' + str(rowcount)
    accession_list.append(rowcount_total)
    dict['Accession'] = accession_list
    output_df = pd.DataFrame.from_dict(dict, orient='columns', dtype=None, columns=None)
    now = datetime.datetime.now()
    now_str = now.strftime("%d%m%y_%H-%M-%S")
    output_df.to_csv(f'suppressed_analysis_details.log.{now_str}.txt', header=None, index=False, sep=' ', mode='w')
    print(output_df)

#############
##  MAIN   ##
#############
database = args.database.lower()
if args.action.lower() == 'suppress':
    action = '5'
elif args.action.lower() == 'cancel':
    action = '3'
else:
    sys.stderr.write(f"the term {args.action} is not allowed, please use suppress or cancel for the action argument \n")
    exit(1)

if database == 'erapro':
    #Connecting to ERAPRO
    sys.stderr.write("Connecting to ERAPRO...\n")
    db_conn = setup_connection()
    sys.stderr.write("Querying ERAPRO ..........\n")
    suppression(db_conn, action)

elif database == 'enapro':
    #Connecting to ENAPRO
    sys.stderr.write("Connecting to ENAPRO...\n")
    db_conn = setup_connection()
    sys.stderr.write("Querying ENAPRO ..........\n")
    suppression(db_conn, action)
