import smtplib, ssl

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
import argparse, hashlib, os, subprocess, sys, time, getpass, smtplib, ssl
from datetime import datetime
import pandas as pd
import shutil
import fnmatch
import configparser
parser = argparse.ArgumentParser(prog='Emailer.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + ============================================================ +
        |  European Nucleotide Archive (ENA) data flow monitoring Tool |
        |                                                              |
        |           Emailer system for the INSDC sync workflow       |
        + =========================================================== +
This script is used to analyse the data from NCBI and ENA that been produced by data_fetch_script.py and data_analysis_script.py.        
        """)
parser.add_argument('-f', '--file', help='path for the input files', type=str, required=True)
parser.add_argument('-g', '--ignore', help='list of accession to be ignored in ENAPRO and ERAPRO calculations', type=str, required=True)
parser.add_argument('-c', '--config', help='config file path', type=str, required=True)
args = parser.parse_args()


"""
    Files Uploading 
"""
def uploading_files():
    # upload raw data
    adv_reads = pd.read_csv(f"{args.file}/ENA.read_experiment.log.txt", sep="\t", header=None, names=['accession', 'date'])
    NCBI_reads = pd.read_csv(f"{args.file}/NCBI.sra.log.txt", sep="\t", header=None, names=['run_accession', 'experiment accession', 'date'])
    adv_seq = pd.read_csv(f"{args.file}/ENA.sequence.log.txt", sep="\t", header=None, names=['accession', 'date'])
    NCBI_seq = pd.read_csv(f"{args.file}/NCBI.nucleotide.log.txt", sep="\t", header=None, names=['accession'])
    portal_reads = pd.read_csv(f"{args.file}/Covid19DataPortal.raw-reads.log.txt", sep="\t", header=None, names=['accession'])
    portal_seq = pd.read_csv(f"{args.file}/Covid19DataPortal.sequences.log.txt", sep="\t", header=None,  names=['accession'])
    ebi_reads = pd.read_csv(f"{args.file}/EBIsearch.sra-experiment-covid19.log.txt", sep="\t", header=None,  names=['accession', 'date'])
    ebi_seq = pd.read_csv(f"{args.file}/EBIsearch.embl-covid19.log.txt", sep="\t", header=None,  names=['accession', 'date'])
    # upload analysed data
    NCBI_vs_adv_reads = pd.read_csv(f"{args.file}/NCBI_vs_ENA_reads.log.txt", sep="\t", header=None, names=['accession'])
    NCBI_vs_adv_seq = pd.read_csv(f"{args.file}/NCBI_vs_ENA_sequences.log.txt", sep="\t", header=None, names=['accession'])
    adv_vs_ebi_reads = pd.read_csv(f"{args.file}/ENAadvanced_vs_EBIsearch_reads.log.txt", sep="\t", header=None, names=['accession', 'date'])
    adv_vs_ebi_seq = pd.read_csv(f"{args.file}/ENAadvanced_vs_EBIsearch_sequences.log.txt", sep="\t", header=None, names=['accession', 'date'])
    ebi_vs_adv_reads = pd.read_csv(f"{args.file}/EBIsearch_vs_ENAadvanced_reads.log.txt", sep="\t", header=None, names=['accession', 'date'])
    ebi_vs_adv_seq = pd.read_csv(f"{args.file}/EBIsearch_vs_ENAadvanced_sequences.log.txt", sep="\t", header=None, names=['accession', 'date'])
    portal_duplicate_reads = pd.read_csv(f"{args.file}/Duplicates.Covid19Portal.reads.log.txt", sep="\t", header=None, names=['accession'])
    portal_duplicate_seq = pd.read_csv(f"{args.file}/Duplicates.Covid19Portal.sequences.log.txt", sep="\t", header=None, names=['accession'])
    portal_vs_adv_reads = pd.read_csv(f"{args.file}/Covid19Portal.vs.ENA.advanced.reads.log.txt", sep="\t", header=None, names=['accession', 'date'])
    portal_vs_adv_seq = pd.read_csv(f"{args.file}/Covid19Portal.vs.ENA.advanced.sequences.log.txt", sep="\t", header=None, names=['accession', 'date'])
    inENAPRO = pd.read_csv(f"{args.file}/analysis.inENAPRO.sequences.log.txt", sep="\t", header=None, names=['accession', 'First_public','Last_public', 'status_id','presentation_status'])
    noENAPRO = pd.read_csv(f"{args.file}/analysis.noENAPRO.sequences.log.txt", sep="\t", header=None, names=['accession', 'date'])
    noENAPRO= filterNCBI_data(noENAPRO,"analysis.noENAPRO.sequences.filtered.log", 'sequences')
    inERAPRO = pd.read_csv(f"{args.file}/analysis.inERAPRO.reads.log.txt", sep="\t", header=None, names=['accession', 'status_id', 'First_public', 'Last_updated', 'presentation_status'])
    noERAPRO = pd.read_csv(f"{args.file}/analysis.noERAPRO.reads.log.txt", sep=",", header=None, names=['exp_accession','run_accession', 'date'])
    noERAPRO = noERAPRO.iloc[1: , :]
    noERAPRO= filterNCBI_data(noERAPRO[['run_accession', 'date']],"analysis.noERAPRO.reads.filtered.log", 'reads')


    return [adv_reads,NCBI_reads,adv_seq,NCBI_seq,portal_reads,portal_seq,ebi_reads,ebi_seq,
            NCBI_vs_adv_reads,NCBI_vs_adv_seq,adv_vs_ebi_reads,adv_vs_ebi_seq,ebi_vs_adv_reads,ebi_vs_adv_seq,
            portal_duplicate_reads,portal_duplicate_seq,portal_vs_adv_reads,portal_vs_adv_seq,inENAPRO,noENAPRO,inERAPRO,noERAPRO]


"""
    function to create and send emails
"""

def emailer(msg_reads,msg_seq):
    config = configparser.ConfigParser()
    config.read(args.config)
    port = 587  # For SSL
    password = config['EMAIL_DETAILS']['sender_email_pass']
    try:
        # Create your SMTP session
        smtp = smtplib.SMTP("outgoing.ebi.ac.uk", port)
        # Use TLS to add security
        smtp.starttls()
        # User Authentication
        smtp.login(config['EMAIL_DETAILS']['sender_email_add'], password )
        # Defining The Message
        HEAD = """
\n************************************
- THIS IS AN AUTO GENERATED EMAIL -
**************************************\n
Below is a summary report for the INSDC dataflow:
Note: for NCBI-ENA Mirroring, data submitted to NCBI today is not included in the report, as mirroring takes at least 24 hrs"""

        SIG = f"""
For further details please check the logs in the following path (IN CODON): 
{os.path.abspath(args.file)}

If you have any concerns please contact azyoud@ebi.ac.uk or reply to this email

Thank you !!!
        """


        TEXT = f'{msg_reads}\n{msg_seq}'

        now = datetime.now()
        now_str = now.strftime("%d-%m-%Y")

        SUBJECT = f"Weekly SARS-CoV-2 INSDC dataflow Report_{now_str}"
        message = 'Subject: {}\n\n{}\n{}\n\n{}'.format(SUBJECT,HEAD, TEXT, SIG)
        # Sending the Email
        emails_list = tuple(email for email in config['EMAIL_DETAILS']['emails_list'].split(','))
        smtp.sendmail(config['EMAIL_DETAILS']['sender_email_add'], (emails_list), message)
        # Terminating the session
        smtp.quit()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong....", ex)


"""
    function to construct the message body
"""


def message(adv_reads,NCBI_reads,adv_seq,NCBI_seq,portal_reads,portal_seq,ebi_reads,ebi_seq,
            NCBI_vs_adv_reads,NCBI_vs_adv_seq,adv_vs_ebi_reads,adv_vs_ebi_seq,ebi_vs_adv_reads,ebi_vs_adv_seq,
            portal_duplicate_reads,portal_duplicate_seq,portal_vs_adv_reads,portal_vs_adv_seq,inENAPRO,noENAPRO,inERAPRO,noERAPRO, database):
    if database == 'Reads':
        NCBI_database = 'SRA database'
        NCBI_data = NCBI_reads
        adv_search = adv_reads
        portal_data = portal_reads
        ebi_search = ebi_reads
        inSQL = inERAPRO
        noSQL = noERAPRO
        NCBI_vs_adv = NCBI_vs_adv_reads
        if len(noSQL) > (len(NCBI_data) * 0.1/100):
            NCBI_vs_adv_critical = f"High missing read numbers from AdvancedSearch API comparing to NCBI: {len(noSQL)}; \n (Please see below for details)"
        else:
            NCBI_vs_adv_critical = None
        adv_vs_ebi = adv_vs_ebi_reads
        ebi_vs_adv = ebi_vs_adv_reads
        if len(ebi_vs_adv) > (len(adv_search) * 10/100):
            ebi_vs_adv_critical = f"High missing read numbers from EBIsearch API : {len(ebi_vs_adv)}"
        else:
            ebi_vs_adv_critical = None
        portal_duplicates = portal_duplicate_reads
        if len(portal_duplicates) > 0 :
            duplicate_critical = f"Duplicated read data found in COVID-19 data Portal: {len(portal_duplicates)}"
        else:
            duplicate_critical = None
        portal_vs_adv = portal_vs_adv_reads
        if len(portal_vs_adv) > (len(adv_search) * 10/100):
            portal_vs_adv_critical = f"High missing read numbers from Portal API:  {len(portal_vs_adv)}"
        else:
            portal_vs_adv_critical = None
        missing_list_report = f'The remaining accessions -if exist- will be reported'

    else:
        NCBI_database = 'Nucleotide database'
        NCBI_data = NCBI_seq
        adv_search = adv_seq
        portal_data = portal_seq
        ebi_search = ebi_seq
        inSQL = inENAPRO
        noSQL = noENAPRO
        NCBI_vs_adv = NCBI_vs_adv_seq
        if len(noSQL) > (len(NCBI_data) * 0.1/100):
            NCBI_vs_adv_critical = f"High missing sequence numbers from AdvancedSearch API comparing to NCBI: {len(noSQL)}; \n (Please see below for details)"
        else:
            NCBI_vs_adv_critical = None
        adv_vs_ebi = adv_vs_ebi_seq
        ebi_vs_adv = ebi_vs_adv_seq
        if len(ebi_vs_adv) > (len(adv_search) * 10/100):
            ebi_vs_adv_critical = f"High missing sequence numbers from EBIsearch API : {len(ebi_vs_adv)}"
        else:
            ebi_vs_adv_critical = None
        portal_duplicates = portal_duplicate_seq
        if len(portal_duplicates) > 0 :
            duplicate_critical = f"Duplicated sequence data found in COVID-19 data Portal : {len(portal_duplicates)}"
        else:
            duplicate_critical = None
        portal_vs_adv = portal_vs_adv_seq
        if len(portal_vs_adv) > (len(adv_search) * 10/100):
            portal_vs_adv_critical = f"High missing sequence numbers from Portal API:  {len(portal_vs_adv)}"
        else:
            portal_vs_adv_critical = None
        missing_list_report= f'The remaining accessions list has been sent to /nfs/production/cochrane/ena/covid19/missing-records (CODON) to be investigated '

    if any([NCBI_vs_adv_critical, portal_vs_adv_critical, duplicate_critical, ebi_vs_adv_critical]):
        critical_msg = f'''Critical Issues:
    {'' if NCBI_vs_adv_critical is None else f"{NCBI_vs_adv_critical}"}
    {'' if portal_vs_adv_critical is None else f"{portal_vs_adv_critical}"}
    {'' if duplicate_critical is None else f"{duplicate_critical}"}
    {'' if ebi_vs_adv_critical is None else f"{ebi_vs_adv_critical}"}'''
    else:
        critical_msg = ''
    msg= f'''
{critical_msg}
For {database} data: 
-------------------------------------------------------------------------------------------------------------------------------------
General 
    * Number of {database} in NCBI ({NCBI_database}) is: {len(NCBI_data)}
    * Number of {database} in ENA Advanced Search is:  {len(adv_search)}
    * Number of {database} in EBI Search is:  {len(ebi_search)}
-------------------------------------------------------------------------------------------------------------------------------------
COVID-19 data Portal 
    * Number of {database} in COVID-19 data portal is: {len(portal_data)} with {len(portal_duplicates)} duplicated values
    * Number of {database} found in ENA advanced search but missing in COVID-19 data portal is : {len(portal_vs_adv)} 
--------------------------------------------------------------------------------------------------------------------------------------
NCBI - ENA Mirroring 
    * Number of public {database} found in NCBI ({NCBI_database}) but missing in ENA advanced search is: {len(NCBI_vs_adv)} {database}.
          -Currently, {int((len(inSQL)/len(NCBI_vs_adv))*100)}% out of these missing values ({len(inSQL)}) are still under processing.
          -While the remainder ({len(noSQL)}) have not been mirrored 
                Note: -{missing_list_report}.
--------------------------------------------------------------------------------------------------------------------------------------
EBI Search 
    * Number of {database} found in EBI search but missing in ENA advanced search is:  {len(ebi_vs_adv)-1}
    * Number of {database} found in ENA advanced search but missing in EBI search is:  {len(adv_vs_ebi)-1}
--------------------------------------------------------------------------------------------------------------------------------------
    '''
    return msg


def filterNCBI_data(df,file_name, database):
    ignore = pd.read_csv(args.ignore, sep="\t", header=None, names=['accession'])
    ignore_acc =[]
    for acc in ignore['accession']:
        ignore_acc.append(acc)
    data = []
    now = datetime.now()
    now_str = now.strftime("%Y/%m/%d")
    for index, row in df.iterrows():
        if row[0] in ignore_acc or fnmatch.fnmatch(row[0].strip(), '^[A-Za-z]{6}[0-9]{2}+0+|^[A-Za-z]{4}[0-9]{2}+0+') or fnmatch.fnmatch(row[0], '[0-9]*') or len(row[0]) < 8:
            continue
        if row[1] == now_str:
            continue
        else:
            dict = {'accession': row[0], 'release_date': row[1]}
            data.append(dict)
    df_filter = pd.DataFrame(data)
    now_str = now.strftime("%d%m%y")
    df_filter.to_csv(f"{args.file}/{file_name}_{now_str}.txt", index=False)
    if database == 'sequences':
        shutil.copy(f"{args.file}/{file_name}_{now_str}.txt", f"/nfs/production/cochrane/ena/covid19/missing-records/")

    return df_filter


#############
##  MAIN   ##
#############

data = uploading_files()

read_msg = message(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],
        data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21], 'Reads')

seq_msg = message(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],
        data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21], 'Sequences')

emailer(read_msg,seq_msg)
