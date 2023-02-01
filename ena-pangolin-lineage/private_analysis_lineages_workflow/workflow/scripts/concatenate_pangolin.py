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


import argparse
import requests, sys
import pandas as pd
import glob
import os
import cx_Oracle

parser = argparse.ArgumentParser(prog='concatenate_pangolin.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        | 		 European Nucleotide Archive (ENA)
		   part of Private analysis pangolin lineages Tool      |
        |                                                              |
        |             Tool to concate pangolin csv output              |  |
        |                                                              |
        + =========================================================== +  """)

parser.add_argument('-f', '--file', help='csv files input directory', type=str, required=True)
parser.add_argument('-o', '--output', help='output directory', type=str, required=True)
parser.add_argument('-s', '--serviceName', help='service name, eg: ERAPRO, ENAPRO', type=str, required=True)
parser.add_argument('-p', '--portal', help='portal number', type=int, required=True)
parser.add_argument('-h', '--host_link', help='database host link', type=str, required=True)
args = parser.parse_args()


"""
Request username and password for databases
"""
def get_oracle_usr_pwd():
    return ['era_reader', 'reader']



"""
Setup the connection to ERAPRO.
"""
def setup_connection():
    oracle_usr, oracle_pwd = get_oracle_usr_pwd()
    client_lib_dir = os.getenv('ORACLE_CLIENT_LIB')
    if not client_lib_dir or not os.path.isdir(client_lib_dir):
        sys.stderr.write("ERROR: Environment variable $ORACLE_CLIENT_LIB must point at a valid directory\n")
        exit(1)
    cx_Oracle.init_oracle_client(lib_dir=client_lib_dir)
    connection = None
    try:
        dsn = cx_Oracle.makedsn(args.host_link, args.portal, service_name=args.serviceName)
        connection = cx_Oracle.connect(oracle_usr, oracle_pwd, dsn, encoding="UTF-8")
        return connection
    except cx_Oracle.Error as error:
        print(error)


"""
Query ENAPRO dataset, process the data and fetching release date from NCBI nucleotide database. Print to a file.
"""
def fetch_and_filter_erz(connection, run_acc_list):
   # This Part is for querying ERAPRO
    c = connection.cursor()
    acc_list = []
    acc_list_run = []
    for accession in run_acc_list:
        c.execute(f"select data_file_owner_id from webin_file w join\
        (select ay.analysis_id from analysis ay join\
        (select * from analysis_sample a join\
        (select * from run_sample where run_id in ('{accession}')) r\
        on a.sample_id = r.sample_id) ars on ay.analysis_id = ars.analysis_id\
        where ay.status_id !=5 and ay.bioproject_id in\
        ('PRJEB48024','PRJEB48256','PRJEB48419','PRJEB48025','PRJEB39014')) aar\
        on w.data_file_owner_id = aar.analysis_id\
        where w.data_file_format = 'FASTA' and upload_file_path like '%consensus.fasta.gz%'")
        for row in c:
            acc_list.append(row[0])
            acc_list_run.append(accession)
    run_df = pd.DataFrame({'run_accession': acc_list_run})
    erz_df = pd.DataFrame({'analysis_accession': acc_list})
    acc_df = pd.concat([run_df, erz_df], ignore_index=False, axis=1)

    return acc_df
    # conn.close()




def concat_csv():
    files = os.path.join(args.file, "pango_lineages.*.csv")
    files = glob.glob(files)
    df = pd.concat(map(pd.read_csv, files), ignore_index=True)
    return df

def formatting_dataframe(df):
    run_acc_list =[]
    for row in df['taxon']:
        parsed_row = row.split('_')
        run_acc = parsed_row[0].strip('CDP:')
        run_acc_list.append(run_acc)
    db_conn = setup_connection()
    acc_df = fetch_and_filter_erz(db_conn, run_acc_list)
    run_df = pd.DataFrame({'run_accession':run_acc_list})
    df = pd.concat([df, run_df], ignore_index=False, axis=1)
    df_merged = df.join(acc_df.set_index('run_accession'), on ='run_accession', how='left')
    df_final=df_merged.dropna(subset = ['analysis_accession'])
    df_final.to_csv(f'{args.output}', index=False)
    print(f'Concatenate all csv files in {args.file} into {args.output}')
#############
##  MAIN   ##
#############

df = concat_csv()
formatting_dataframe(df)
