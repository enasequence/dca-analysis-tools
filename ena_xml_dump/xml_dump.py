#!/usr/bin/env python3.7

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

import argparse, os
import requests, sys
import cx_Oracle
import pandas as pd
import fnmatch
import configparser

parser = argparse.ArgumentParser(prog='xml_dump.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |               European Nucleotide Archive (ENA)              |
        |                                                              |
        |         Tool to to fetch objects xml from ENA database       |
        + =========================================================== +        
        """)
parser.add_argument('-f', '--file', help='path for the input files', type=str, required=False)
parser.add_argument('-t', '--type', help='data type', type=str, required=True)
parser.add_argument('-acc', '--accession', help='accession number', type=str, required=False)
parser.add_argument('-c', '--config', help='config file path', type=str, required=True)
parser.add_argument('-o', '--output', help='Output directory', type=str, required=True)
args = parser.parse_args()

# generate and create the output directory
def create_outdir():
    outdir = f"{args.output}"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    return outdir

"""
Setup the connection to ENAPRO and ERAPRO. 
"""
def setup_connection():
    # ConfigFile
    config = configparser.ConfigParser()
    config.read(args.config)
    oracle_usr, oracle_pwd = [config['ERAPRO_DETAILS']['userName'], config['ERAPRO_DETAILS']['password']]   #get_oracle_usr_pwd
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



"""
    Query ERAPRO dataset and processing the data. Print to a file.
"""

def fetch_and_filter(connection, acc, database):
    # This Part is for querying ERAPRO
        for accession in acc['accession']:
            if accession == 'accession':
                continue
            elif fnmatch.fnmatch(accession, 'PRJ*'):
                print(accession)
                SQL_query(connection, accession, database)
            elif (fnmatch.fnmatch(accession,'ERS*') or fnmatch.fnmatch(accession,'SRS*')) and database == 'sample':
                print(accession)
                SQL_query(connection,accession,database)
            elif fnmatch.fnmatch(accession,'ERZ*') and database == 'analysis':
                print(accession)
                SQL_query(connection,accession, database)
            elif (fnmatch.fnmatch(accession,'ERR*') or fnmatch.fnmatch(accession,'SRR*')) and database == 'run':
                print(accession)
                SQL_query(connection,accession, database)
            elif (fnmatch.fnmatch(accession,'ERX*') or fnmatch.fnmatch(accession,'SRX*')) and database == 'experiment':
                print(accession)
                SQL_query(connection,accession, database)
            elif (fnmatch.fnmatch(accession,'ERP*') or fnmatch.fnmatch(accession,'SRP*')) and database == 'study':
                print(accession)
                SQL_query(connection,accession, database)
            else:
                print(f'The accession type ({database}) and the accession number ({accession}) are not matching')
                exit(1)


def SQL_query(connection,accession, database):
    outdir = create_outdir()
    c = connection.cursor()
    with open(f"{outdir}/{database}_output.xml", "a") as f:
        if fnmatch.fnmatch(accession, 'PRJ*') and not database == 'project':
            if database == 'sample' or database == 'all':
                c.execute(
                    f"""select fs.sample_xml.getClobVal() from sample fs join (select distinct ass.sample_id from analysis a join
                    (select s.sample_id, s.sample_xml, asa.analysis_id from analysis_sample asa 
                    join sample s on asa.sample_id = s.sample_id)ass  
                    on a.analysis_id = ass.analysis_id where a.bioproject_id 
                    in ('{accession}') union
                    select distinct sr.sample_id from sample sr join
                    (select * from run_sample rs join(select * from run r join
                    (select * from experiment ex 
                    join study st on st.study_id = ex.study_id 
                    where st.project_id in ('{accession}')) exs
                    on r.experiment_id = exs.experiment_id)rf 
                    on rs.run_id = rf.run_id) rsf on sr.sample_id = rsf.sample_id) fi 
                    on fs.sample_id = fi.sample_id where fs.status_id !=5 and fs.status_id !=3""")
                for row in c:
                    f.write(str(row[0]) + "\n")
            elif database == 'experiment' or database == 'all':
                    c.execute(
                        f"""select exf.experiment_xml.getClobVal() from experiment exf 
                            join(select distinct ex.experiment_id from experiment ex join study st 
                            on ex.study_id = st.study_id where st.project_id in ('{accession}'))fi 
                            on exf.experiment_id = fi.experiment_id where exf.status_id !=5 and exf.status_id !=3""")
                    for row in c:
                        f.write(str(row[0]) + "\n")
            elif database == 'run' or database == 'all':
                c.execute(
                    f"""select rf.run_xml.getClobVal() from run rf join(select distinct run_id from run r 
                        join(select * from experiment ex join study st on ex.study_id = st.study_id
                        where st.project_id in ('{accession}')) exst 
                        on r.experiment_id = exst.experiment_id) fi on rf.run_id = fi.run_id where rf.status_id !=5 and rf.status_id !=3""")
                for row in c:
                    f.write(str(row[0]) + "\n")

            elif database == 'study' or database == 'all':
                c.execute(
                    f"select s.study_xml.getClobVal() from study s join project p on s.project_id = p.project_id where p.project_id in ('{accession}') and s.status_id !=5 and s.status_id !=3")
                for row in c:
                    f.write(str(row[0]) + "\n")

            elif database == 'analysis' or database == 'all':
                c.execute(
                    f"select (analysis_xml).getClobVal() from analysis where bioproject_id in ('{accession}') and status_id !=5 and status_id !=3")
                for row in c:
                    f.write(str(row[0]) + "\n")

            elif database == 'all':
                c.execute(
                    f"select (project_xml).getClobVal() from project where project_id in ('{accession}') and status_id !=5 and status_id !=3")
                for row in c:
                    f.write(str(row[0]) + "\n")


        else:
            c.execute(
                f"select ({database}_xml).getClobVal() from {database} where {database}_id in ('{accession}') and status_id and !=5 status_id !=3")
            for row in c:
                f.write(str(row[0]) + "\n")

def file_upload(database):
    accession = pd.read_csv(args.file, header=None, names=['accession'])
    # Querying ERAPRO
    db_conn = setup_connection()
    sys.stderr.write("Querying ERAPRO ..........\n")
    fetch_and_filter(db_conn, accession, database)


def accessions(database):
    acc_list =[]
    for acc in args.accession.split(','):
        acc_list.append(acc)
    acc_df = pd.DataFrame({'accession': acc_list})
    # Querying ERAPRO
    db_conn = setup_connection()
    sys.stderr.write("Querying ERAPRO ..........\n")
    fetch_and_filter(db_conn, acc_df, database)


############
#    MAIN   #
#           #
############

#database = input("please indicate the dataset type, ex: ENAPRO or ERAPRO: ").lower()

if args.type.lower() == 'samples':
    database = 'sample'
elif args.type.lower() == 'analyses':
    database = 'analysis'
elif args.type.lower() == 'runs':
    database = 'run'
elif args.type.lower() == 'experiments':
    database = 'experiment'
elif args.type.lower() == 'projects':
    database = 'project'
elif args.type.lower() == 'studies':
    database = 'study'
else:
    database = args.type.lower()


# Uploading Files
if args.file and not args.accession:
    acc = file_upload(database)


elif args.accession and not args.file:
    acc = accessions(database)


elif args.file and args.accession:
    print ("please include one accession list (--file/-f or --accession/-acc )")
    exit(1)
else:
    print("please include accession number either as a list in a .txt file (--file/-f : path to the file) or as an accession directly using the -acc/--accesison flag")
    exit(1)

